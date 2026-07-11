import generated from './structures.generated.json';

export interface StructureMetrics {
  file: string;
  n_atoms: number;
  n_bonds: number;
  gen?: number;
  composition?: Record<string, number>;
  mw?: number;
  rg_heavy?: number;
  rg_all?: number;
  R_sphere?: number;
  Rh?: number;
  diameter?: number;
  asphericity?: number;
  acylindricity?: number;
  kappa2?: number;
  eigenvalues?: number[];
  vdw_volume?: number;
  V_sphere?: number;
  void_fraction?: number;
  sasa?: number;
  density?: number;
}

export interface StructureEntry {
  id: string;
  name: string;
  core: StructureMetrics | null;
  monomer: StructureMetrics | null;
  generations: StructureMetrics[];
}

export const structures = generated as unknown as Record<string, StructureEntry>;

export function getStructure(id: string): StructureEntry | undefined {
  return structures[id];
}

/** Molecular formula string, e.g. "C302 H608 N122 O60" (Hill-ish order). */
export function formula(comp?: Record<string, number>): string {
  if (!comp) return '';
  const order = ['C', 'H', 'N', 'O', 'P', 'S', 'Si', 'Cl', 'F', 'Br'];
  const keys = Object.keys(comp).sort((a, b) => {
    const ia = order.indexOf(a), ib = order.indexOf(b);
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
  });
  return keys.map((k) => `${k}${comp[k]}`).join(' ');
}

function shapeLabel(d?: number): string {
  if (d == null) return '';
  if (d < 0.02) return 'near-perfect sphere';
  if (d < 0.05) return 'slightly aspherical';
  if (d < 0.15) return 'moderately aspherical';
  if (d < 0.4) return 'aspherical';
  return 'strongly aspherical';
}

export interface MetricRow { label: string; value: string; note?: string; }

/** Curated, display-ready characteristic rows computed by the UDB module. */
export function metricRows(m: StructureMetrics): MetricRow[] {
  const rows: MetricRow[] = [];
  const num = (v: number | undefined, d = 2) => (v == null ? '-' : v.toFixed(d));
  rows.push({ label: 'Atoms', value: m.n_atoms.toLocaleString() });
  rows.push({ label: 'Bonds', value: m.n_bonds.toLocaleString() });
  if (m.composition) rows.push({ label: 'Formula', value: formula(m.composition) });
  if (m.mw != null) rows.push({ label: 'Mol. weight', value: `${m.mw.toFixed(1)} Da`, note: `${(m.mw / 1000).toFixed(2)} kDa` });
  if (m.rg_heavy != null) rows.push({ label: 'Rg (heavy)', value: `${num(m.rg_heavy)} Å` });
  if (m.diameter != null) rows.push({ label: 'Diameter', value: `${num(m.diameter)} Å`, note: `${(m.diameter / 10).toFixed(2)} nm` });
  if (m.Rh != null) rows.push({ label: 'Hydrodyn. radius Rh', value: `${num(m.Rh)} Å` });
  if (m.asphericity != null) rows.push({ label: 'Asphericity δ', value: num(m.asphericity, 3), note: shapeLabel(m.asphericity) });
  if (m.acylindricity != null) rows.push({ label: 'Acylindricity c', value: num(m.acylindricity, 3) });
  if (m.kappa2 != null) rows.push({ label: 'Shape anisotropy κ²', value: num(m.kappa2, 3) });
  if (m.vdw_volume != null) rows.push({ label: 'vdW volume', value: `${m.vdw_volume.toFixed(0)} Å³` });
  if (m.void_fraction != null) rows.push({ label: 'Void fraction', value: `${(m.void_fraction * 100).toFixed(1)} %` });
  if (m.sasa != null) rows.push({ label: 'SASA', value: `${m.sasa.toFixed(0)} Å²` });
  if (m.density != null) rows.push({ label: 'Density', value: `${m.density.toFixed(3)} g/cm³` });
  return rows;
}

/** element -> Jmol-ish colour for legends */
export const ELEMENT_COLORS: Record<string, string> = {
  C: '#909090', H: '#e6e6e6', N: '#3050F8', O: '#FF2010',
  P: '#FF8000', S: '#FFFF30', Si: '#F0C8A0', Cl: '#1FF01F',
};
