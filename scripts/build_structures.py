#!/usr/bin/env python3
"""
Build the live-structure dataset for the UDB website.

For every dendrimer type it:
  - parses the pure core (core_typed.mol2) and monomer (monomer_typed.mol2)
  - parses each AMBER/GAFF-minimised generation (dendrimer_<t>_gen<N>_min_gaff.mol2),
    taking generations contiguously from gen1 and STOPPING at the first missing one
  - runs the real UDB characterization module (udb_characterization.py) on each
  - copies the .mol2 files into public/mol2/ under clean names
  - writes src/data/structures.generated.json consumed by the site at build time

Run:  python3 scripts/build_structures.py
"""
import os, re, sys, json, shutil

HERE      = os.path.dirname(os.path.abspath(__file__))
WEB       = os.path.dirname(HERE)
BUILDS    = "/home/hirushawalgampaya/Downloads/udb-software/v1.0/Builds"
CHAR_DIR  = "/home/hirushawalgampaya/Downloads/udb-software/v1.0/Tests"
GOLDEN    = os.path.join(CHAR_DIR, "golden")
PUB_MOL2  = os.path.join(WEB, "public", "mol2")
OUT_JSON  = os.path.join(WEB, "src", "data", "structures.generated.json")

sys.path.insert(0, CHAR_DIR)
import udb_characterization as U  # noqa: E402

# folder -> site id / display name
TYPES = [
    ("PAMAM",        "pamam",        "PAMAM"),
    ("PPI",          "ppi",          "PPI"),
    ("Carbosilane",  "carbosilane",  "Carbosilane"),
    ("Phosphorus",   "phosphorus",   "Phosphorus"),
    ("PLL",          "pll",          "PLL"),
    ("Polyester",    "polyester",    "Polyester"),
    ("Polyglycerol", "polyglycerol", "Polyglycerol"),
]


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


def gens_for(folder):
    """Contiguous gen numbers with a *_min_gaff.mol2, starting at 1, stop at first gap."""
    present = set()
    for f in os.listdir(folder):
        mo = re.match(r"dendrimer_.*_gen(\d+)_min_gaff\.mol2$", f)
        if mo:
            present.add(int(mo.group(1)))
    out, n = [], 1
    while n in present:
        out.append(n); n += 1
    return out


def main():
    os.makedirs(PUB_MOL2, exist_ok=True)
    dataset = {}
    for folder, tid, name in TYPES:
        fdir = os.path.join(BUILDS, folder)
        if not os.path.isdir(fdir):
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

        # contiguous minimised generations
        gens = gens_for(fdir)
        prefix = f"dendrimer_{tid}_gen"
        for n in gens:
            src = os.path.join(fdir, f"{prefix}{n}_min_gaff.mol2")
            atoms, nb = parse_mol2(src)
            dst_name = f"{tid}-g{n}.mol2"
            shutil.copyfile(src, os.path.join(PUB_MOL2, dst_name))
            data = characterize(atoms, nb)
            data["gen"] = n
            data["file"] = f"/mol2/{dst_name}"
            entry["generations"].append(data)
            print(f"  G{n}       {data['n_atoms']:5d} atoms  Rg={data.get('rg_heavy',0):.2f}  "
                  f"asph={data.get('asphericity',0):.3f}  -> {dst_name}")
        dataset[tid] = entry

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(dataset, fh, indent=1)
    print(f"\nwrote {OUT_JSON}")

    # ---- validate against golden (match by n_atoms) ----
    print("\n=== validation vs golden ===")
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
