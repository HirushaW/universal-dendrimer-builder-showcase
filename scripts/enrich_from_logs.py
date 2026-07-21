#!/usr/bin/env python3
"""
Enrich the live-structure dataset with build- and simulation-setup metadata that
only exists in the UDB build logs (Structures/<Type>/*.txt), not in the .mol2
geometry that build_structures.py already characterises.

For every family it extracts:
  - per-type build parameters (from the final "Starting build: <Type>" block):
    UDB version, core binding atoms, monomer attachment atom + labile mode,
    terminal atoms, bond length/angle, branching factor, parameterization,
    output formats, generations requested
  - force field + water model (from the NAMD packaging block)
  - per-generation MD setup: solvent box size, temperature, production length,
    timestep, rigidBonds mode, Langevin piston period
  - per-generation build record: grafting sites, monomers added, as-built atom
    and bond counts, terminal groups, branching junctions, as-built MW / Rg /
    solvated Rg / asphericity, the validation score, and the Rg shift produced
    by the inter-generational AMBER minimisation

It merges these into src/data/structures.generated.json IN PLACE, adding a
top-level `build` object per type and `md` + `log` objects on each generation.
Geometry metrics computed from the coordinates are never modified.

A family folder may hold SEVERAL logs (e.g. PAMAM keeps both the v1.0 run, which
is the only one carrying NAMD/MD blocks, and the current v1.1 build). All are
parsed and merged oldest-version-first, so the newest build wins per field while
still-valid detail from an older run is retained. Within one log, blocks from
other families can appear before the real build (the Polyglycerol log opens with
Polyester packaging lines), so per-generation data is read only from the slice
that follows the LAST "Starting build: <Type>" line.

Run:  python3 scripts/enrich_from_logs.py
"""
import os, re, json, glob

HERE      = os.path.dirname(os.path.abspath(__file__))
WEB       = os.path.dirname(HERE)
STRUCT_DIR = os.path.join(WEB, "Structures")
OUT_JSON  = os.path.join(WEB, "src", "data", "structures.generated.json")

# site id -> (display name used inside the log, on-disk folder base)
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


def resolve_logs(base, name):
    """Every build log in a type folder, ordered oldest build first.

    Ranking key is the UDB version stamped on the log's own "Starting build"
    line, falling back to file mtime, so merging in this order lets the most
    recent build overwrite older values field by field.
    """
    folder = resolve_folder(base)
    if not folder:
        return []
    out = []
    for p in sorted(glob.glob(os.path.join(folder, "*.txt"))):
        b = os.path.basename(p).lower()
        if "gui_settings" in b or b == "readme.txt":
            continue
        lines = read_lines(p)
        ver = log_version(lines, name)
        if ver is None and not starts(lines, name):
            continue                       # not a build log for this family
        out.append((ver or 0.0, os.path.getmtime(p), p))
    out.sort()
    return [p for _, _, p in out]


def read_lines(path):
    return open(path, encoding="utf-8", errors="replace").read().splitlines()


def starts(lines, name):
    """Indices of every 'Starting build: <name>' line."""
    return [i for i, ln in enumerate(lines)
            if re.search(rf"Starting build:\s+{re.escape(name)}\b", ln)]


def log_version(lines, name):
    """Version on the last 'Starting build: <name>  vX.Y' line, as a float."""
    ver = None
    for i in starts(lines, name):
        if m := re.search(r"\bv(\d+(?:\.\d+)?)", lines[i]):
            ver = float(m.group(1))
    return ver


def build_slice(lines, name):
    """Lines from the last 'Starting build: <name>' onwards (the real build)."""
    idx = starts(lines, name)
    return lines[idx[-1]:] if idx else lines


def _int_list(s):
    return [int(x) for x in re.findall(r"-?\d+", s)]


def _str_list(s):
    return re.findall(r"'([^']*)'", s)


def _num(s):
    """'39,591' -> 39591.0"""
    return float(s.replace(",", ""))


def parse_build(lines, name):
    """Return the build-parameter dict from the LAST 'Starting build' block."""
    idx = starts(lines, name)
    if not idx:
        return None
    block = lines[idx[-1]: idx[-1] + 25]
    b = {}
    if m := re.search(r"\bv(\d+(?:\.\d+)?)", block[0]):
        b["udb_version"] = m.group(1)
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
        elif m := re.match(r"Generations to save\s*:\s*(\[.+\])", s):
            b["generations_built"] = _int_list(m.group(1))
        elif m := re.match(r"Output formats\s*:\s*(\[.+\])", s):
            b["output_formats"] = _str_list(m.group(1))
        elif m := re.match(r"Parameterization\s*:\s*(.+)", s):
            b["parameterization"] = m.group(1).strip()
    return b or None


def parse_md(lines, name):
    """{gen: md-dict} from the NAMD packaging blocks, which are family-tagged and
    so can be read from the whole log. Last occurrence per generation wins."""
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


def parse_generations(lines):
    """{gen: log-dict} for the build slice of one family.

    Walks the generation sections in order, so unlabelled sub-blocks ('G6
    complete:', the MW/Rg summary line) attach to the generation whose header
    was seen last. The closing BUILD COMPLETE table is applied afterwards and
    is authoritative for the headline numbers.
    """
    gens, cur, minfrom = {}, None, None

    def slot(n):
        return gens.setdefault(n, {})

    for ln in lines:
        s = ln.strip()

        if m := re.match(r"GENERATION (\d+)\s*\|", s):
            cur = int(m.group(1)); continue

        # "G1: 4 core sites x 2 = 8 monomers"  /  "G6: 128 index-tracked terminal sites"
        if m := re.match(r"G(\d+):\s*(\d+)\s*core sites x\s*(\d+)\s*=\s*(\d+)\s*monomers", s):
            g = slot(int(m.group(1)))
            g["sites"] = int(m.group(2)); g["monomers"] = int(m.group(4)); continue
        if m := re.match(r"G(\d+):\s*(\d+)\s*index-tracked terminal sites", s):
            slot(int(m.group(1)))["sites"] = int(m.group(2)); continue

        if m := re.match(r"G(\d+) complete:", s):
            cur = int(m.group(1)); continue
        if cur is not None:
            if m := re.match(r"Sites\s*:\s*(\d+)", s):
                slot(cur)["sites"] = int(m.group(1)); continue
            if m := re.match(r"Monomers\s*:\s*(\d+)", s):
                slot(cur)["monomers"] = int(m.group(1)); continue
            if m := re.match(r"Total atoms\s*:\s*(\d+)", s):
                slot(cur)["atoms_built"] = int(m.group(1)); continue
            if m := re.match(r"Total bonds\s*:\s*(\d+)", s):
                slot(cur)["bonds_built"] = int(m.group(1)); continue

        if m := re.match(r"VALIDATION G(\d+)\s*\((\d+)/(\d+) passed\)", s):
            g = slot(int(m.group(1)))
            g["validation_passed"] = int(m.group(2))
            g["validation_total"] = int(m.group(3)); continue

        # "MW=39,591 Da  Rg=22.13 A  Rg_solv=26.56 A  delta=0.0382  Term=505  Branch=1"
        if m := re.match(r"MW=([\d,]+) Da\s+Rg=([\d.]+) A\s+Rg_solv=([\d.]+) A\s+"
                         r"delta=([\d.]+)\s+Term=(\d+)\s+Branch=(\d+)", s):
            if cur is not None:
                g = slot(cur)
                g["mw_built"] = _num(m.group(1))
                g["rg_built"] = float(m.group(2))
                g["rg_solvated"] = float(m.group(3))
                g["delta_built"] = float(m.group(4))
                g["terminals"] = int(m.group(5))
                g["branch_points"] = int(m.group(6))
            continue

        # inter-generational AMBER minimisation: attributed to the SOURCE gen
        if m := re.match(r"INTERGENERATIONAL MIN\s+G(\d+)\s*→\s*G(\d+)", s):
            minfrom = int(m.group(1)); continue
        if minfrom is not None:
            if m := re.match(r"\[IntergenMin\] AMBER coords accepted:\s*Rg\s*([\d.]+)\s*→\s*([\d.]+)", s):
                g = slot(minfrom)
                g["min_rg_before"] = float(m.group(1))
                g["min_rg_after"] = float(m.group(2))
                minfrom = None; continue
            if "No minimized coords obtained" in s:
                minfrom = None; continue

        # closing summary table: "G5    3753     19,579     18.28    21.93   0.0550   10/10"
        if m := re.match(r"G(\d+)\s+(\d+)\s+([\d,]+)\s+([\d.]+)\s+([\d.]+)\s+"
                         r"([\d.]+)\s+(\d+)/(\d+)\s*$", s):
            g = slot(int(m.group(1)))
            g["atoms_built"] = int(m.group(2))
            g["mw_built"] = _num(m.group(3))
            g["rg_built"] = float(m.group(4))
            g["rg_solvated"] = float(m.group(5))
            g["delta_built"] = float(m.group(6))
            g["validation_passed"] = int(m.group(7))
            g["validation_total"] = int(m.group(8))
            continue

    return gens


def merge_gen(dst, src):
    """dst[gen] |= src[gen] for every generation in src."""
    for n, block in src.items():
        dst.setdefault(n, {}).update(block)
    return dst


def main():
    data = json.load(open(OUT_JSON))
    for tid, name, base in TYPES:
        paths = resolve_logs(base, name)
        if not paths:
            print(f"skip {name}: no log under Structures/{base}"); continue
        if tid not in data:
            print(f"skip {name}: not in dataset"); continue

        build, md, glog = {}, {}, {}
        for path in paths:                      # oldest build first, newest wins
            lines = read_lines(path)
            sl = build_slice(lines, name)
            if b := parse_build(lines, name):
                build.update(b)
            merge_gen(md, parse_md(lines, name))
            merge_gen(glog, parse_generations(sl))

        # promote FF/water to the type-level build block (constant across gens)
        any_md = next(iter(md.values()), {})
        for k in ("force_field", "water_model"):
            if k in any_md:
                build[k] = any_md[k]

        # merge so a leaner log (build recipe only, no MD block) never wipes richer
        # data already present for an unchanged family
        data[tid]["build"] = {**data[tid].get("build", {}), **build}

        n_md = n_log = 0
        for g in data[tid]["generations"]:
            n = g.get("gen")
            if n in md:
                block = {k: v for k, v in md[n].items()
                         if k not in ("force_field", "water_model")}
                if block:
                    g["md"] = {**g.get("md", {}), **block}
                    n_md += 1
            if n in glog:
                g["log"] = {**g.get("log", {}), **glog[n]}
                n_log += 1

        total = len(data[tid]["generations"])
        print(f"{name:13s} logs={len(paths)}  build={len(build)} fields  "
              f"md->{n_md}/{total} gens  log->{n_log}/{total} gens")

    json.dump(data, open(OUT_JSON, "w"), indent=1)
    print(f"\nwrote {OUT_JSON}")


if __name__ == "__main__":
    main()
