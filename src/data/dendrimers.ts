export interface DendrimerGeneration {
  gen: string;
  src: string;
  atoms: string;
}

export interface DendrimerType {
  id: string;
  name: string;
  full: string;
  coreLabel: string;
  color: string;
  description: string;
  chemistry: string;
  applications: string;
  forceField: string;
  generations: DendrimerGeneration[];
  monomerUrl: string;
  coreUrl: string;
}

export const dendrimers: DendrimerType[] = [
  {
    id: 'pamam',
    name: 'PAMAM',
    full: 'Polyamidoamine',
    coreLabel: 'EDA core',
    color: 'cyan',
    description: 'The most widely studied dendrimer family. EDA (ethylenediamine) core with amidoamine branching units and primary amine surface groups. The benchmark system for all computational dendrimer tools.',
    chemistry: 'Ethylenediamine core · amidoamine repeating units · –NH₂ surface groups · branching factor 2',
    applications: 'Gene delivery, drug encapsulation, MRI contrast agents, antibacterial coatings',
    forceField: 'GAFF2 + Fragment BCC (full support)',
    generations: [
      { gen: 'G1', src: '/images/real-pamam-g1.png', atoms: '84' },
      { gen: 'G2', src: '/images/real-pamam-g2.png', atoms: '228' },
      { gen: 'G3', src: '/images/real-pamam-g3.png', atoms: '516' },
      { gen: 'G4', src: '/images/real-pamam-g4.png', atoms: '1,108' },
    ],
    monomerUrl: '/mol2/pamam-monomer.pdb',
    coreUrl: '/mol2/pamam-core.pdb',
  },
  {
    id: 'ppi',
    name: 'PPI',
    full: 'Polypropylenimine',
    coreLabel: 'DAB core',
    color: 'sky',
    description: 'DAB (1,4-diaminobutane) core with propylenimine branching. Dense primary amine surface. Closely related to PAMAM but with a more compact, hydrophobic interior and higher charge density.',
    chemistry: 'Diaminobutane core · propylenimine repeating units · –NH₂ surface groups · branching factor 2',
    applications: 'Nucleic acid delivery, antimicrobial agents, metal ion chelation, catalysis supports',
    forceField: 'GAFF2 + CGenFF (full support)',
    generations: [
      { gen: 'G1', src: '/images/real-ppi-g1.png', atoms: '~60' },
      { gen: 'G2', src: '/images/real-ppi-g2.png', atoms: '~220' },
      { gen: 'G3', src: '/images/real-ppi-g3.png', atoms: '~700' },
      { gen: 'G4', src: '/images/real-ppi-g4.png', atoms: '~1,400' },
    ],
    monomerUrl: '/mol2/ppi-monomer.pdb',
    coreUrl: '/mol2/ppi-core.pdb',
  },
  {
    id: 'carbosilane',
    name: 'Carbosilane',
    full: 'Carbosilane',
    coreLabel: 'Si–C core',
    color: 'amber',
    description: 'Silicon–carbon backbone dendrimer with a highly flexible, hydrophobic interior. Unique among dendrimers for its organosilicon chemistry. Requires GAFF2 manual bypass, since CGenFF is incompatible with Si atoms.',
    chemistry: 'Si–C branching units · vinyl or allyl termini · hydrophobic interior · high chain flexibility',
    applications: 'Antiviral agents (HIV inhibition), hydrophobic drug carriers, materials science, silicon-based nanodevices',
    forceField: 'GAFF2 manual bypass (CGenFF incompatible with Si)',
    generations: [
      { gen: 'G1', src: '/images/real-carbosilane-g1.png', atoms: '~80' },
      { gen: 'G2', src: '/images/real-carbosilane-g2.png', atoms: '~280' },
      { gen: 'G3', src: '/images/real-carbosilane-g3.png', atoms: '~800' },
      { gen: 'G4', src: '/images/real-carbosilane-g4.png', atoms: '~2,200' },
    ],
    monomerUrl: '/mol2/carbosilane-monomer.pdb',
    coreUrl: '/mol2/carbosilane-core.pdb',
  },
  {
    id: 'phosphorus',
    name: 'Phosphorus',
    full: 'Phosphorus',
    coreLabel: 'P–N core',
    color: 'red',
    description: 'Phosphorus–nitrogen backbone with cyclotriphosphazene or P=N–P repeating units. High density of P and N atoms creates unusual electrostatic surface properties and strong anion-binding capability.',
    chemistry: 'P=N–P branching units · aldehyde or amine termini · high P/N ratio · strong electrostatics',
    applications: 'Immunology (anti-inflammatory), prion disease inhibition, antitumour agents, anion sensing',
    forceField: 'GAFF2 + Gasteiger charges (G3+ requires UFF fallback for P)',
    generations: [
      { gen: 'G1', src: '/images/real-phosphorus-g1.png', atoms: '~120' },
      { gen: 'G2', src: '/images/real-phosphorus-g2.png', atoms: '~350' },
      { gen: 'G3', src: '/images/real-phosphorus-g3.png', atoms: '~650' },
      { gen: 'G4', src: '/images/real-phosphorus-g4.png', atoms: '~1,500' },
    ],
    monomerUrl: '/mol2/phosphorus-monomer.pdb',
    coreUrl: '/mol2/phosphorus-core.pdb',
  },
  {
    id: 'pll',
    name: 'PLL',
    full: 'Poly-L-Lysine',
    coreLabel: 'Lys core',
    color: 'emerald',
    description: 'Amino acid-based dendrimer using L-Lysine as the branching unit. Fully biocompatible and biodegradable. Amenable to a wide range of surface functionalizations for targeted drug and gene delivery.',
    chemistry: 'L-Lysine repeating units · α-amine and ε-amine branching · peptide (amide) backbone · chiral centres',
    applications: 'Drug delivery, gene therapy, tissue engineering scaffolds, antimicrobial peptide mimics',
    forceField: 'GAFF2 + CGenFF (full support)',
    generations: [
      { gen: 'G1', src: '/images/real-pll-g1.png', atoms: '~90' },
      { gen: 'G2', src: '/images/real-pll-g2.png', atoms: '~300' },
      { gen: 'G3', src: '/images/real-pll-g3.png', atoms: '~850' },
      { gen: 'G4', src: '/images/real-pll-g4.png', atoms: '~2,100' },
    ],
    monomerUrl: '/mol2/pll-monomer.pdb',
    coreUrl: '/mol2/pll-core.pdb',
  },
  {
    id: 'polyester',
    name: 'Polyester',
    full: 'Polyester',
    coreLabel: 'Ester core',
    color: 'orange',
    description: 'Ester-linked dendrimer backbone with high hydrolytic degradability under physiological conditions. Ideal for controlled release applications where the dendrimer itself breaks down after drug delivery.',
    chemistry: 'Ester linkages throughout · hydroxyl surface groups · hydrolytically labile backbone · high OH density',
    applications: 'Controlled drug release, biodegradable nanocarriers, prodrug delivery, wound healing',
    forceField: 'GAFF2 + CGenFF (full support)',
    generations: [
      { gen: 'G1', src: '/images/real-polyester-g1.png', atoms: '~80' },
      { gen: 'G2', src: '/images/real-polyester-g2.png', atoms: '~260' },
      { gen: 'G3', src: '/images/real-polyester-g3.png', atoms: '~760' },
      { gen: 'G4', src: '/images/real-polyester-g4.png', atoms: '~2,000' },
    ],
    monomerUrl: '/mol2/polyester-monomer.pdb',
    coreUrl: '/mol2/polyester-core.pdb',
  },
  {
    id: 'polyglycerol',
    name: 'Polyglycerol',
    full: 'Polyglycerol',
    coreLabel: 'Glycerol core',
    color: 'fuchsia',
    description: 'Glycerol-based branching with an exceptionally high density of hydroxyl surface groups. Outstanding water solubility, stealth behaviour, and low cytotoxicity make it a leading platform for biomedical use.',
    chemistry: 'Glycerol repeating units · –OH surface groups · ether backbone · high water solubility · biocompatible',
    applications: 'Stealth nanocarriers, protein-resistant coatings, anti-fouling surfaces, ophthalmic drug delivery',
    forceField: 'GAFF2 + CGenFF (full support)',
    generations: [
      { gen: 'G1', src: '/images/real-polyglycerol-g1.png', atoms: '~70' },
      { gen: 'G2', src: '/images/real-polyglycerol-g2.png', atoms: '~220' },
      { gen: 'G3', src: '/images/real-polyglycerol-g3.png', atoms: '~650' },
      { gen: 'G5', src: '/images/real-polyglycerol-g5.png', atoms: '~5,500' },
    ],
    monomerUrl: '/mol2/polyglycerol-monomer.pdb',
    coreUrl: '/mol2/polyglycerol-core.pdb',
  },
];

export const colorBadge: Record<string, string> = {
  cyan:    'bg-cyan-500/10    text-cyan-300    border-cyan-500/25',
  sky:     'bg-sky-500/10     text-sky-300     border-sky-500/25',
  amber:   'bg-amber-500/10   text-amber-300   border-amber-500/25',
  red:     'bg-red-500/10     text-red-300     border-red-500/25',
  emerald: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/25',
  orange:  'bg-orange-500/10  text-orange-300  border-orange-500/25',
  fuchsia: 'bg-fuchsia-500/10 text-fuchsia-300 border-fuchsia-500/25',
};

export const colorAccent: Record<string, string> = {
  cyan:    'text-cyan-400',
  sky:     'text-sky-400',
  amber:   'text-amber-400',
  red:     'text-red-400',
  emerald: 'text-emerald-400',
  orange:  'text-orange-400',
  fuchsia: 'text-fuchsia-400',
};

export const colorBorder: Record<string, string> = {
  cyan:    'border-cyan-500/30    hover:border-cyan-500/70',
  sky:     'border-sky-500/30     hover:border-sky-500/70',
  amber:   'border-amber-500/30   hover:border-amber-500/70',
  red:     'border-red-500/30     hover:border-red-500/70',
  emerald: 'border-emerald-500/30 hover:border-emerald-500/70',
  orange:  'border-orange-500/30  hover:border-orange-500/70',
  fuchsia: 'border-fuchsia-500/30 hover:border-fuchsia-500/70',
};

export const colorGlow: Record<string, string> = {
  cyan:    'rgba(6,182,212,0.12)',
  sky:     'rgba(14,165,233,0.12)',
  amber:   'rgba(245,158,11,0.12)',
  red:     'rgba(239,68,68,0.12)',
  emerald: 'rgba(16,185,129,0.12)',
  orange:  'rgba(249,115,22,0.12)',
  fuchsia: 'rgba(217,70,239,0.12)',
};
