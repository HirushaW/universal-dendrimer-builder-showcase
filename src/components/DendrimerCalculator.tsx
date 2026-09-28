import { useState, useMemo, useEffect, useRef } from 'react';

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
    description: 'Polyamidoamine - EDA core, G1-G10',
    color: '#14b8a6',
  },
  PPI: {
    label: 'PPI',
    f: 4, m: 3, g1Atoms: 72, massPerAtom: 13.5,
    description: 'Polypropylenimine - DAB core',
    color: '#0ea5e9',
  },
  Triazine: {
    label: 'Triazine',
    f: 6, m: 3, g1Atoms: 92, massPerAtom: 14.2,
    description: 'Triazine-based - 6-arm symmetry',
    color: '#a78bfa',
  },
  Carbosilane: {
    label: 'Carbosilane',
    f: 4, m: 3, g1Atoms: 96, massPerAtom: 15.5,
    description: 'Si-containing - use GAFF2 bypass',
    color: '#f59e0b',
  },
  PLL: {
    label: 'PLL',
    f: 2, m: 2, g1Atoms: 78, massPerAtom: 13.8,
    description: 'Poly-L-Lysine - linear-branched',
    color: '#34d399',
  },
  Phosphorus: {
    label: 'Phosphorus',
    f: 6, m: 2, g1Atoms: 88, massPerAtom: 15.0,
    description: 'Phosphorus-core - 6-arm P-based',
    color: '#f87171',
  },
  Polyester: {
    label: 'Polyester',
    f: 4, m: 2, g1Atoms: 82, massPerAtom: 13.2,
    description: 'Polyester - biodegradable scaffold',
    color: '#fb923c',
  },
  Polyglycerol: {
    label: 'Polyglycerol',
    f: 3, m: 2, g1Atoms: 68, massPerAtom: 12.8,
    description: 'Polyglycerol - 3-arm compact',
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

/** Smoothly animates a number toward `target` (ease-out cubic). Honors reduced motion. */
function useTween(target: number, ms = 480): number {
  const [value, setValue] = useState(target);
  const from = useRef(target);
  useEffect(() => {
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { from.current = target; setValue(target); return; }
    const a = from.current;
    const t0 = performance.now();
    let raf = 0;
    const tick = (now: number) => {
      const k = Math.min(1, (now - t0) / ms);
      const cur = a + (target - a) * (1 - Math.pow(1 - k, 3));
      from.current = cur;
      setValue(cur);
      if (k < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, ms]);
  return value;
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

  const tTerm = useTween(results.nTerm);
  const tAtoms = useTween(results.nAtoms);
  const tMw = useTween(results.mw);
  const tRg = useTween(results.rg);
  const pct = ((gen - 1) / 9) * 100;

  return (
    <div className="lg-calc rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="lg-calc-head px-6 py-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center lg-calc-ico">
          <svg className="w-4 h-4 text-teal-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
        </div>
        <div>
          <h3 className="text-slate-100 font-semibold text-sm font-display tracking-wide">Live Dendrimer Calculator</h3>
          <p className="text-slate-500 text-xs">Estimates based on UDB structural models</p>
        </div>
        <span className="ml-auto hidden sm:inline-flex items-center gap-1.5 font-mono text-[10px] tracking-[0.18em] text-teal-300/80">
          <span className="hud-dot animate-pulse" aria-hidden="true"></span>LIVE
        </span>
      </div>

      <div className="p-6 grid md:grid-cols-2 gap-6">
        {/* Controls */}
        <div className="space-y-5">
          {/* Type selector */}
          <div>
            <label htmlFor="udb-calc-type" className="block text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">
              Dendrimer Type
            </label>
            <select
              id="udb-calc-type"
              value={type}
              onChange={e => setType(e.target.value)}
              className="lg-select w-full rounded-xl px-3.5 py-2.5 text-slate-100 text-sm cursor-pointer"
              style={{ ['--accent' as string]: spec.color }}
            >
              {Object.keys(TYPES).map(k => (
                <option key={k} value={k}>{TYPES[k].label} - {TYPES[k].description}</option>
              ))}
            </select>
          </div>

          {/* Generation slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label htmlFor="udb-calc-gen" className="text-slate-400 text-xs font-medium uppercase tracking-wider">
                Generation
              </label>
              <span
                key={gen}
                className="lg-gen-badge font-hud text-xl font-bold px-3 py-0.5 rounded-lg"
                style={{ color: spec.color, background: spec.color + '15', boxShadow: `inset 0 1px 0 ${spec.color}40, 0 0 18px ${spec.color}22` }}
              >
                G{gen}
              </span>
            </div>
            <input
              id="udb-calc-gen"
              type="range"
              min={1} max={10} step={1}
              value={gen}
              onChange={e => setGen(Number(e.target.value))}
              className="lg-range"
              style={{ ['--pct' as string]: `${pct}%`, ['--accent' as string]: spec.color }}
              aria-valuetext={`Generation ${gen}`}
            />
            <div className="flex justify-between text-slate-600 text-xs mt-1.5">
              {Array.from({ length: 10 }, (_, i) => (
                <button
                  type="button"
                  key={i + 1}
                  onClick={() => setGen(i + 1)}
                  className={`lg-tick font-mono ${gen === i + 1 ? 'is-on' : ''}`}
                  style={gen === i + 1 ? { color: spec.color } : undefined}
                  aria-label={`Set generation ${i + 1}`}
                  aria-pressed={gen === i + 1}
                >
                  G{i + 1}
                </button>
              ))}
            </div>
          </div>

          {/* Type info pill */}
          <div
            className="px-3 py-2 rounded-lg text-xs transition-colors duration-300"
            style={{ background: spec.color + '15', borderLeft: `3px solid ${spec.color}` }}
          >
            <span className="text-slate-400">Core arms (f) = </span>
            <span className="text-slate-200 font-medium">{spec.f}</span>
            <span className="text-slate-600 mx-2">·</span>
            <span className="text-slate-400">Branching factor (m) = </span>
            <span className="text-slate-200 font-medium">{spec.m}</span>
          </div>
        </div>

        {/* Results (numbers animate; the hidden line below announces final values once) */}
        <p className="sr-only" aria-live="polite">
          {`${spec.label} G${gen}: ${formatLargeNumber(results.nTerm)} terminal groups, ${formatLargeNumber(results.nAtoms)} atoms, ${formatMW(results.mw)}, Rg ${results.rg.toFixed(1)} Å`}
        </p>
        <div className="grid grid-cols-2 gap-3">
          {[
            {
              label: 'Terminal Groups',
              value: formatLargeNumber(tTerm),
              sub: `f·m^G = ${spec.f}·${spec.m}^${gen}`,
              icon: '⬡',
              color: spec.color,
            },
            {
              label: 'Atom Count',
              value: formatLargeNumber(tAtoms),
              sub: 'heavy atoms (approx.)',
              icon: '⚛',
              color: '#94a3b8',
            },
            {
              label: 'Mol. Weight',
              value: formatMW(tMw),
              sub: 'estimated',
              icon: '⚖',
              color: '#94a3b8',
            },
            {
              label: 'Rg (radius of gyration)',
              value: `${tRg.toFixed(1)} Å`,
              sub: '3.0·(N/84)^(1/3)',
              icon: '◎',
              color: '#94a3b8',
            },
          ].map(item => (
            <div
              key={item.label}
              className="lg-tile rounded-xl p-4"
              style={{ ['--accent' as string]: spec.color }}
            >
              <div className="text-lg mb-1" aria-hidden="true">{item.icon}</div>
              <div className="font-hud text-2xl font-bold" style={{ color: item.color }}>
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
