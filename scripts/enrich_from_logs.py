#!/usr/bin/env python3
"""
Enrich the live-structure dataset with build- and simulation-setup metadata that
only exists in the UDB build logs (Structures/Data/<Type>.txt), not in the .mol2
geometry that build_structures.py already characterises.

For every log it extracts:
  - per-type build parameters (from the final "Starting build: <Type>" block):
    core binding atoms, monomer attachment atom + labile mode, terminal atoms,
    bond length/angle, branching factor, parameterization, output formats
  - force field + water model (from the NAMD packaging block)
  - per-generation MD setup: solvent box size, temperature, production length,
    timestep, rigidBonds mode, Langevin piston period, and the build-time
    site/monomer counts

It merges these into src/data/structures.generated.json IN PLACE, adding a
top-level `build` object per type and an `md` object on each matching generation.
Existing geometry metrics are never modified.

Logs may contain repeated passes or stray blocks from other families (e.g. the
Polyglycerol log opens with Polyester packaging lines); for every field the LAST
value that matches the target family name wins, mirroring the final build.

Run:  python3 scripts/enrich_from_logs.py
"""
import os, re, json, glob

HERE      = os.path.dirname(os.path.abspath(__file__))
WEB       = os.path.dirname(HERE)
STRUCT_DIR = os.path.join(WEB, "Structures")
OUT_JSON  = os.path.join(WEB, "src", "data", "structures.generated.json")

# site id -> (display name used inside the log, on-disk folder base)
# Each build log now lives inside its type folder, named either "<Name>.txt"
# (newly produced sets) or "Build log <Name>.txt" (earlier sets).
TYPES = [
    ("pamam",        "PAMAM",        "PAMAM"),
    ("ppi",          "PPI",          "PPI"),
    ("carbosilane",  "Carbosilane",  "Carbosilane"),
    ("phosphorus",   "Phosphorus",   "Phosphorus"),
    ("pll",          "PLL",          "PLL"),
    ("polyester",    "Polyester",    "Polyester"),
    ("polyglycerol", "Polyglycerol", "Polyglycerol"),
    ("triazine",     "Triazine",     "Triazene"),
]


def resolve_folder(base):
    """Path for a type folder, tolerating a trailing marker (e.g. 'PPI *')."""
    exact = os.path.join(STRUCT_DIR, base)
    if os.path.isdir(exact):
        return exact
    for h in sorted(glob.glob(os.path.join(STRUCT_DIR, base + " *"))) + \
             sorted(glob.glob(os.path.join(STRUCT_DIR, base + "*"))):
        if os.path.isdir(h):
            return h
    return None


def resolve_log(base, name):
    """Locate the build log inside a type folder."""
    folder = resolve_folder(base)
    if not folder:
        return None
    for cand in (f"{name}.txt", f"Build log {name}.txt", f"Build log {base}.txt"):
        p = os.path.join(folder, cand)
        if os.path.exists(p):
            return p
    for p in sorted(glob.glob(os.path.join(folder, "*.txt"))):
        b = os.path.basename(p).lower()
        if "gui_settings" in b or b == "readme.txt":
            continue
        return p
    return None


def _int_list(s):
    return [int(x) for x in re.findall(r"-?\d+", s)]


def _str_list(s):
    return re.findall(r"'([^']*)'", s)


def parse_build(lines, name):
    """Return the build-parameter dict from the LAST 'Starting build: <name>' block."""
    starts = [i for i, ln in enumerate(lines)
              if re.search(rf"Starting build:\s+{re.escape(name)}\b", ln)]
    if not starts:
        return None
    block = lines[starts[-1]: starts[-1] + 25]
    b = {}
    for ln in block:
        s = ln.strip()
        if m := re.match(r"Core binding atoms\s*:\s*(.+)", s):
            b["core_binding_atoms"] = _int_list(m.group(1))
        elif m := re.match(r"Monomer input\s*:\s*(\S+)\s*\(labile:\s*(\[[^\]]*\])\s*mode:\s*(\w+)", s):
            b["monomer_attach"] = m.group(1)
            b["labile_atoms"] = _str_list(m.group(2))
            b["labile_mode"] = m.group(3)
        elif m := re.match(r"Terminal atoms\s*:\s*(.+)", s):
            b["terminal_atoms"] = _str_list(m.group(1))
        elif m := re.match(r"Bond length / angle\s*:\s*([\d.]+)\s*A\s*/\s*([\d.]+)\s*deg", s):
            b["bond_length"] = float(m.group(1))
            b["bond_angle"] = float(m.group(2))
        elif m := re.match(r"Branching factor\s*:\s*(\d+)", s):
            b["branching_factor"] = int(m.group(1))
        elif m := re.match(r"Output formats\s*:\s*(\[.+\])", s):
            b["output_formats"] = _str_list(m.group(1))
        elif m := re.match(r"Parameterization\s*:\s*(.+)", s):
            b["parameterization"] = m.group(1).strip()
    return b or None


def parse_md(lines, name):
    """Return {gen: md-dict} from the NAMD packaging blocks for this family.
    Last occurrence per generation wins."""
    md = {}
    cur = None
    for ln in lines:
        s = ln.strip()
        if m := re.match(rf"Type:\s*{re.escape(name)}\s+G(\d+)\s*\|\s*FF:\s*(\S+)\s*\|\s*Water:\s*(\S+)", s):
            cur = int(m.group(1))
            md[cur] = {"force_field": m.group(2), "water_model": m.group(3)}
        elif cur is not None and (m := re.match(r"Box:\s*~?([\d.]+)\s*A\s*\|\s*Temp:\s*([\d.]+)\s*K\s*\|\s*Prod:\s*([\d.]+)\s*ns", s)):
            md[cur]["box"] = float(m.group(1))
            md[cur]["temperature"] = float(m.group(2))
            md[cur]["production_ns"] = float(m.group(3))
        elif cur is not None and (m := re.match(r"rigidBonds:\s*(\S+)\s*\|\s*ts:\s*([\d.]+)\s*fs\s*\|\s*Piston:\s*([\d.]+)\s*ps", s)):
            md[cur]["rigid_bonds"] = m.group(1)
            md[cur]["timestep_fs"] = float(m.group(2))
            md[cur]["piston_ps"] = float(m.group(3))
            cur = None
    return md


def parse_counts(lines):
    """Return {gen: {sites, monomers}} from 'G1: 4 core sites x 2 = 8 monomers'.
    Last occurrence per generation wins."""
    counts = {}
    for ln in lines:
        if m := re.search(r"G(\d+):\s*(\d+)\s*core sites x\s*(\d+)\s*=\s*(\d+)\s*monomers", ln):
            counts[int(m.group(1))] = {"sites": int(m.group(2)), "monomers": int(m.group(4))}
    return counts


def main():
    data = json.load(open(OUT_JSON))
    for tid, name, base in TYPES:
        path = resolve_log(base, name)
        if not path:
            print(f"skip {name}: no log under Structures/{base}"); continue
        if tid not in data:
            print(f"skip {name}: not in dataset"); continue
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()

        build = parse_build(lines, name) or {}
        md = parse_md(lines, name)
        counts = parse_counts(lines)
        # promote FF/water to the type-level build block (constant across gens)
        any_md = next(iter(md.values()), {})
        if "force_field" in any_md:
            build["force_field"] = any_md["force_field"]
        if "water_model" in any_md:
            build["water_model"] = any_md["water_model"]

        # merge so a leaner log (build recipe only, no MD block) never wipes richer
        # data already present for an unchanged family
        data[tid]["build"] = {**data[tid].get("build", {}), **build}

        attached = 0
        for g in data[tid]["generations"]:
            n = g.get("gen")
            block = {}
            if n in md:
                block.update({k: v for k, v in md[n].items()
                              if k not in ("force_field", "water_model")})
            if n in counts:
                block.update(counts[n])
            if block:
                g["md"] = {**g.get("md", {}), **block}
                attached += 1
        print(f"{name:13s} build={len(build)} fields  md->{attached}/{len(data[tid]['generations'])} gens")

    json.dump(data, open(OUT_JSON, "w"), indent=1)
    print(f"\nwrote {OUT_JSON}")


if __name__ == "__main__":
    main()
