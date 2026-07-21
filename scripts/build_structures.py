#!/usr/bin/env python3
"""
Build the live-structure dataset for the UDB website.

For every dendrimer type it:
  - parses the pure core (core_typed.mol2) and monomer (monomer_typed.mol2)
  - resolves every generation up to MAX_GEN (6) through a provenance fallback
    chain, so a family is always shown complete to G6:
        1. dendrimer_<t>_gen<N>_min_gaff.mol2   AMBER/GAFF-minimised (preferred)
        2. dendrimer_<t>_gen<N>_min.pdb         AMBER-minimised, PDB only
        3. dendrimer_<t>_gen<N>_typed.mol2      as-built, GAFF-typed
        4. dendrimer_<t>_gen<N>.pdb             as-built, plain PDB
    The chosen tier is recorded on each generation as `source`, so the site can
    label which geometries are minimised and which are as-built.
  - runs the real UDB characterization module (udb_characterization.py) on each
  - copies the .mol2 files into public/mol2/ under clean names
  - writes src/data/structures.generated.json consumed by the site at build time

Run:  python3 scripts/build_structures.py
"""
import os, re, sys, json, glob, shutil

HERE      = os.path.dirname(os.path.abspath(__file__))
WEB       = os.path.dirname(HERE)
# Structures live in the website repo itself (the newly produced set). Do NOT read
# from any external build folder — the site visualises exactly what is in ./Structures.
BUILDS    = os.path.join(WEB, "Structures")
CHAR_DIR  = "/home/hirushawalgampaya/Downloads/udb-software/Old/v1.0/mods"
GOLDEN    = os.path.join(CHAR_DIR, "golden")
PUB_MOL2  = os.path.join(WEB, "public", "mol2")
MAX_GEN   = 6                      # every family is published through G6
OUT_JSON  = os.path.join(WEB, "src", "data", "structures.generated.json")

sys.path.insert(0, CHAR_DIR)
import udb_characterization as U  # noqa: E402

# folder -> site id / display name. Mol2 file prefix is auto-detected per folder
# (e.g. Triazene's files are named dendrimer_triazine_*), so the site id need not
# match the on-disk stem.
TYPES = [
    ("PAMAM",        "pamam",        "PAMAM"),
    ("PPI",          "ppi",          "PPI"),
    ("Carbosilane",  "carbosilane",  "Carbosilane"),
    ("Phosphorus",   "phosphorus",   "Phosphorus"),
    ("PLL",          "pll",          "PLL"),
    ("Polyester",    "polyester",    "Polyester"),
    ("Polyglycerol", "polyglycerol", "Polyglycerol"),
    ("Triazene",     "triazine",     "Triazine"),
]


def resolve_folder(folder):
    """Return the on-disk path for a type folder. Tolerates a trailing marker the
    user may append to an unchanged set (e.g. 'PPI *'), so the pipeline works
    whether or not folders were tagged. Prefers an exact match."""
    exact = os.path.join(BUILDS, folder)
    if os.path.isdir(exact):
        return exact
    for h in sorted(glob.glob(os.path.join(BUILDS, folder + " *"))) + \
             sorted(glob.glob(os.path.join(BUILDS, folder + "*"))):
        if os.path.isdir(h):
            return h
    return None


def detect_stem(folder):
    """Auto-detect the 'dendrimer_<stem>' prefix from the generation files in a
    folder (minimised first, then as-built). Returns e.g. 'dendrimer_triazine'."""
    names = sorted(os.listdir(folder))
    for pattern in (r"(dendrimer_.+?)_gen\d+_min_gaff\.mol2$",
                    r"(dendrimer_.+?)_gen\d+_typed\.mol2$",
                    r"(dendrimer_.+?)_gen\d+\.pdb$"):
        for f in names:
            mo = re.match(pattern, f)
            if mo:
                return mo.group(1)
    return None


def parse_mol2(path):
    """Return (atoms, n_bonds). atoms = list of dicts {idx,name,type,x,y,z,charge}."""
    atoms, n_bonds = [], 0
    section = None
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("@<TRIPOS>"):
                section = s.split(">", 1)[1].strip().upper()
                continue
            if not s:
                continue
            if section == "ATOM":
                p = s.split()
                if len(p) < 6:
                    continue
                try:
                    atoms.append({
                        "idx": int(p[0]), "name": p[1], "type": p[5],
                        "x": float(p[2]), "y": float(p[3]), "z": float(p[4]),
                        "charge": p[8] if len(p) > 8 else "0.0",
                    })
                except ValueError:
                    continue
            elif section == "BOND":
                n_bonds += 1
    return atoms, n_bonds


def parse_pdb(path):
    """Return (atoms, n_bonds) for a PDB. Used only when no MOL2 exists for a
    generation: there are no GAFF types or charges, so vdW radii fall back to
    Bondi element radii inside the characterization module. Bonds are counted
    from CONECT records (each pair once); absent CONECT gives 0."""
    atoms, bonds = [], set()
    with open(path) as fh:
        for line in fh:
            rec = line[:6]
            if rec in ("ATOM  ", "HETATM"):
                try:
                    atoms.append({
                        "idx": int(line[6:11]), "name": line[12:16].strip(),
                        "type": "",
                        "x": float(line[30:38]), "y": float(line[38:46]),
                        "z": float(line[46:54]), "charge": "0.0",
                    })
                except ValueError:
                    continue
            elif rec == "CONECT":
                nums = line[6:].split()
                if len(nums) >= 2:
                    a = nums[0]
                    for b in nums[1:]:
                        bonds.add((min(a, b), max(a, b)))
    return atoms, len(bonds)


def parse_structure(path):
    """Parse a MOL2 or PDB by extension."""
    return parse_pdb(path) if path.lower().endswith(".pdb") else parse_mol2(path)


def characterize(atoms, n_bonds):
    """Compute the full metric set using the real UDB module. Guarded per-metric."""
    m = {"n_atoms": len(atoms), "n_bonds": n_bonds}

    def g(fn, *a, key=None):
        try:
            return fn(*a)
        except Exception as e:                       # noqa: BLE001
            if key:
                print(f"      ! {key}: {e}")
            return None

    comp = g(U.atom_composition, atoms, key="composition") or {}
    # composition may be {'C':.., ...} or list; normalise to dict of int
    if isinstance(comp, dict):
        m["composition"] = {k: int(v) for k, v in comp.items() if v}
    else:
        m["composition"] = {}

    m["mw"]        = g(U.molecular_weight, atoms, key="mw")
    m["rg_heavy"]  = g(U.radius_of_gyration_heavy, atoms, key="rg_heavy")
    m["rg_all"]    = g(U.radius_of_gyration, atoms, key="rg_all")

    shape = g(U.shape_tensor_and_eigenvalues, atoms, key="eigs")
    eigs = shape[0] if shape is not None else None   # (eigs, G matrix)
    if eigs is not None:
        m["eigenvalues"]  = [float(x) for x in eigs]
        m["asphericity"]  = g(U.asphericity, eigs)
        m["acylindricity"] = g(U.acylindricity, eigs)
        m["kappa2"]       = g(U.relative_shape_anisotropy, eigs)

    if m.get("rg_heavy"):
        R = g(U.bounding_sphere_radius, m["rg_heavy"])
        m["R_sphere"]  = R
        m["Rh"]        = g(U.hydrodynamic_radius, m["rg_heavy"])
        m["diameter"]  = (2 * R) if R else None
        Vs = g(U.bounding_sphere_volume, R) if R else None
        m["V_sphere"]  = Vs
        Vv = g(U.vdw_volume_mc, atoms, key="vdw_volume")
        m["vdw_volume"] = Vv
        if Vv and Vs:
            m["void_fraction"] = g(U.void_fraction, Vv, Vs)
        # density g/cm^3 from MW / V_sphere
        if m.get("mw") and Vs:
            m["density"] = (m["mw"] / 6.02214076e23) / (Vs * 1e-24)

    m["sasa"] = g(U.sasa_shrake_rupley, atoms, key="sasa")
    return {k: v for k, v in m.items() if v is not None}


# geometry provenance, best first: (filename suffix, source id, label)
SOURCE_CHAIN = [
    ("_min_gaff.mol2", "amber_min",     "AMBER-minimised"),
    ("_min.pdb",       "amber_min_pdb", "AMBER-minimised"),
    ("_typed.mol2",    "as_built",      "as-built"),
    (".pdb",           "as_built_pdb",  "as-built"),
]


def gens_for(folder, stem):
    """Resolve every generation 1..MAX_GEN present in `folder`.

    Returns [(gen, path, source_id, source_label)]. Each generation takes the
    best geometry available to it (see SOURCE_CHAIN), so families whose AMBER
    minimisation only reached G4 still publish a complete G1-G6 series from
    their as-built coordinates. Generations with no file at all are skipped.
    """
    out = []
    for n in range(1, MAX_GEN + 1):
        for suffix, sid, label in SOURCE_CHAIN:
            path = os.path.join(folder, f"{stem}_gen{n}{suffix}")
            if os.path.exists(path):
                out.append((n, path, sid, label))
                break
    return out


def main():
    # `--only a,b,c` rebuilds just those site ids and keeps every other family's
    # entry from the existing dataset untouched (geometry + any enrichment).
    only = None
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == "--only" and i + 1 < len(argv):
            only = {t.strip().lower() for t in argv[i + 1].split(",") if t.strip()}

    os.makedirs(PUB_MOL2, exist_ok=True)
    dataset, prior = {}, {}
    if os.path.exists(OUT_JSON):
        try:
            prior = json.load(open(OUT_JSON))
        except Exception:                                # noqa: BLE001
            prior = {}
    if only and prior:
        dataset = prior
        print(f"subset rebuild: {sorted(only)} (keeping "
              f"{sorted(set(dataset) - only)})")
    for folder, tid, name in TYPES:
        if only and tid not in only:
            continue
        fdir = resolve_folder(folder)
        if not fdir:
            print(f"skip {name}: no folder"); continue
        print(f"\n=== {name} ({tid}) ===")
        entry = {"id": tid, "name": name, "core": None, "monomer": None, "generations": []}

        # core + monomer (pure, typed)
        for kind, fname in (("core", "core_typed.mol2"), ("monomer", "monomer_typed.mol2")):
            src = os.path.join(fdir, fname)
            if os.path.exists(src):
                atoms, nb = parse_mol2(src)
                dst_name = f"{tid}-{kind}.mol2"
                shutil.copyfile(src, os.path.join(PUB_MOL2, dst_name))
                data = characterize(atoms, nb)
                data["file"] = f"/mol2/{dst_name}"
                entry[kind] = data
                print(f"  {kind:8s} {data['n_atoms']:5d} atoms -> {dst_name}")

        # full generation series (G1..G6), each at its best available geometry
        stem = detect_stem(fdir) or f"dendrimer_{tid}"
        for n, src, sid, label in gens_for(fdir, stem):
            atoms, nb = parse_structure(src)
            ext = ".pdb" if src.lower().endswith(".pdb") else ".mol2"
            dst_name = f"{tid}-g{n}{ext}"
            shutil.copyfile(src, os.path.join(PUB_MOL2, dst_name))
            data = characterize(atoms, nb)
            data["gen"] = n
            data["file"] = f"/mol2/{dst_name}"
            data["source"] = sid
            data["source_label"] = label
            entry["generations"].append(data)
            print(f"  G{n}       {data['n_atoms']:5d} atoms  Rg={data.get('rg_heavy',0):.2f}  "
                  f"asph={data.get('asphericity',0):.3f}  [{label}] -> {dst_name}")

        # carry forward log-derived metadata (build recipe, per-generation MD and
        # build records). Geometry is always recomputed here; enrich_from_logs.py
        # re-derives the metadata afterwards and overwrites whatever it can still
        # find in the current logs, so this only preserves fields whose source log
        # is no longer shipped with the structure set.
        old = prior.get(tid, {})
        if old.get("build"):
            entry["build"] = old["build"]
        old_gens = {g.get("gen"): g for g in old.get("generations", [])}
        for g in entry["generations"]:
            og = old_gens.get(g["gen"], {})
            for key in ("md", "log"):
                if og.get(key):
                    g[key] = og[key]
        dataset[tid] = entry

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(dataset, fh, indent=1)
    print(f"\nwrote {OUT_JSON}")

    # ---- validate against golden (match by n_atoms) ----
    print("\n=== validation vs golden ===")
    if not os.path.isdir(GOLDEN):
        print(f"  (skipped: no golden dir at {GOLDEN})")
        return
    by_atoms = {}
    for e in dataset.values():
        for g in e["generations"]:
            by_atoms.setdefault(e["name"], {})[g["n_atoms"]] = g
    for gf in sorted(os.listdir(GOLDEN)):
        fam = gf.split("_g")[0]
        gold = json.load(open(os.path.join(GOLDEN, gf)))
        na = gold.get("n_atoms")
        mine = by_atoms.get(fam, {}).get(na)
        if not mine:
            print(f"  {gf:22s} n={na}: no matching computed structure"); continue
        def cmp(k):
            a, b = gold.get(k), mine.get(k)
            if a is None or b is None: return f"{k}=?"
            d = abs(a - b) / (abs(a) + 1e-9) * 100
            return f"{k} Δ{d:4.1f}%"
        print(f"  {gf:22s} n={na}: " + "  ".join(cmp(k) for k in
              ("rg_heavy", "asphericity", "sasa", "vdw_volume", "void_fraction", "mw")))


if __name__ == "__main__":
    main()
