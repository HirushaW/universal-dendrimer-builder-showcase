import { useState, useMemo } from 'react';

interface DendrimerSpec {
  label: string;
  f: number;  // core functionality (primary arms)
  m: number;  // branching multiplicity per generation
  g1Atoms: number;  // approximate atom count at G1
  massPerAtom: number;  // average Da per atom
  description: string;
  color: string;
}

const TYPES: Record<string, DendrimerSpec> = {
  PAMAM: {
    label: 'PAMAM',
    f: 4, m: 2, g1Atoms: 84, massPerAtom: 14.0,
    description: 'Polyamidoamine (EDA core, G1–G10)',
    color: '#22d3ee',   // cyan-400 — distinct from sky/emerald
  },
  PPI: {
    label: 'PPI',
    f: 4, m: 3, g1Atoms: 72, massPerAtom: 13.5,
    description: 'Polypropylenimine (DAB core)',
    color: '#0ea5e9',
  },
  Triazine: {
    label: 'Triazine',
    f: 6, m: 3, g1Atoms: 92, massPerAtom: 14.2,
    description: 'Triazine-based (6-arm symmetry)',
    color: '#a78bfa',
  },
  Carbosilane: {
    label: 'Carbosilane',
    f: 4, m: 3, g1Atoms: 96, massPerAtom: 15.5,
    description: 'Si-containing (use GAFF2 bypass)',
    color: '#f59e0b',
  },
  PLL: {
    label: 'PLL',
    f: 2, m: 2, g1Atoms: 78, massPerAtom: 13.8,
    description: 'Poly-L-Lysine (linear-branched)',
    color: '#34d399',
  },
  Phosphorus: {
    label: 'Phosphorus',
    f: 6, m: 2, g1Atoms: 88, massPerAtom: 15.0,
    description: 'Phosphorus-core (6-arm P-based)',
    color: '#f87171',
  },
  Polyester: {
    label: 'Polyester',
    f: 4, m: 2, g1Atoms: 82, massPerAtom: 13.2,
    description: 'Polyester (biodegradable scaffold)',
    color: '#fb923c',
  },
  Polyglycerol: {
    label: 'Polyglycerol',
    f: 3, m: 2, g1Atoms: 68, massPerAtom: 12.8,
    description: 'Polyglycerol (3-arm compact)',
    color: '#e879f9',
  },
  Custom: {
    label: 'Custom',
    f: 4, m: 2, g1Atoms: 84, massPerAtom: 14.0,
    description: 'User-defined type',
    color: '#94a3b8',
  },
};

function formatLargeNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'k';
  return Math.round(n).toLocaleString();
}

function formatMW(da: number): string {
  if (da >= 1_000_000) return (da / 1_000_000).toFixed(2) + ' MDa';
  if (da >= 1_000) return (da / 1_000).toFixed(1) + ' kDa';
  return Math.round(da) + ' Da';
}

export default function DendrimerCalculator() {
  const [type, setType] = useState<string>('PAMAM');
  const [gen, setGen] = useState<number>(3);

  const spec = TYPES[type];

  const results = useMemo(() => {
    const { f, m, g1Atoms, massPerAtom } = spec;

    // Number of terminal groups: f * m^G
    const nTerm = f * Math.pow(m, gen);

    // Atom count: scale from G1 using power-law fit from PAMAM reference data
    // N_atoms = g1Atoms * (nTerm / (f*m))^1.276
    // The exponent 1.276 is derived from PAMAM benchmarks (G1=84, G3=516, G6=4548)
    const nTermG1 = f * m;
    const nAtoms = Math.round(g1Atoms * Math.pow(nTerm / nTermG1, 1.276));

    // Molecular weight estimate
    const mw = nAtoms * massPerAtom;

    // Radius of gyration: Rg = 3.0 * (N/84)^(1/3) Å (PAMAM calibrated)
    const rg = 3.0 * Math.pow(nAtoms / 84, 1 / 3);

    return { nTerm, nAtoms, mw, rg };
  }, [type, gen, spec]);

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-sky-500/10 to-slate-900 border-b border-slate-700 px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-sky-500/20 flex items-center justify-center">
          <svg className="w-4 h-4 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
        </div>
        <div>
          <h3 className="text-slate-100 font-semibold text-sm">Live Dendrimer Calculator</h3>
          <p className="text-slate-500 text-xs">Estimates based on UDB structural models</p>
        </div>
      </div>

      <div className="p-6 grid md:grid-cols-2 gap-6">
        {/* Controls */}
        <div className="space-y-5">
          {/* Type selector */}
          <div>
            <label className="block text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">
              Dendrimer Type
            </label>
            <select
              value={type}
              onChange={e => setType(e.target.value)}
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2.5 text-slate-100 text-sm focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500/30 appearance-none cursor-pointer"
            >
              {Object.keys(TYPES).map(k => (
                <option key={k} value={k}>{TYPES[k].label}: {TYPES[k].description}</option>
              ))}
            </select>
          </div>

          {/* Generation slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-slate-400 text-xs font-medium uppercase tracking-wider">
                Generation
              </label>
              <span
                className="text-xl font-bold px-3 py-0.5 rounded-lg"
                style={{ color: spec.color, background: spec.color + '15' }}
              >
                G{gen}
              </span>
            </div>
            <input
              type="range"
              min={1} max={10} step={1}
              value={gen}
              onChange={e => setGen(Number(e.target.value))}
              className="w-full accent-sky-500 cursor-pointer"
            />
            <div className="flex justify-between text-slate-600 text-xs mt-1">
              {Array.from({ length: 10 }, (_, i) => (
                <span key={i + 1} className={gen === i + 1 ? 'text-emerald-400' : ''}>G{i+1}</span>
              ))}
            </div>
          </div>

          {/* Type info pill */}
          <div
            className="px-3 py-2 rounded-lg text-xs"
            style={{ background: spec.color + '15', borderLeft: `3px solid ${spec.color}` }}
          >
            <span className="text-slate-400">Core arms (f) = </span>
            <span className="text-slate-200 font-medium">{spec.f}</span>
            <span className="text-slate-600 mx-2">·</span>
            <span className="text-slate-400">Branching factor (m) = </span>
            <span className="text-slate-200 font-medium">{spec.m}</span>
          </div>
        </div>

        {/* Results */}
        <div className="grid grid-cols-2 gap-3">
          {[
            {
              label: 'Terminal Groups',
              value: formatLargeNumber(results.nTerm),
              sub: `f·m^G = ${spec.f}·${spec.m}^${gen}`,
              icon: '⬡',
              color: spec.color,
            },
            {
              label: 'Atom Count',
              value: formatLargeNumber(results.nAtoms),
              sub: 'heavy atoms (approx.)',
              icon: '⚛',
              color: '#94a3b8',
            },
            {
              label: 'Mol. Weight',
              value: formatMW(results.mw),
              sub: 'estimated',
              icon: '⚖',
              color: '#94a3b8',
            },
            {
              label: 'Rg (radius of gyration)',
              value: `${results.rg.toFixed(1)} Å`,
              sub: '3.0·(N/84)^(1/3)',
              icon: '◎',
              color: '#94a3b8',
            },
          ].map(item => (
            <div
              key={item.label}
              className="bg-slate-800 rounded-xl p-4 border border-slate-700"
            >
              <div className="text-lg mb-1">{item.icon}</div>
              <div className="text-2xl font-bold" style={{ color: item.color }}>
                {item.value}
              </div>
              <div className="text-slate-400 text-xs mt-1">{item.label}</div>
              <div className="text-slate-600 text-xs font-mono mt-0.5">{item.sub}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="px-6 pb-4">
        <p className="text-slate-600 text-xs">
          Estimates use structural scaling formulas calibrated against PAMAM benchmarks (Maiti et al. 2004).
          Values are approximate; run UDB for exact atom counts, AMBER-minimized structures, and NAMD trajectories.
        </p>
      </div>
    </div>
  );
}
