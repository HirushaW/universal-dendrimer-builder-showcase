import { useEffect, useRef } from 'react';

/* ──────────────────────────────────────────────────────────────────────────
 * DendrimerHero
 * A live, GPU-cheap canvas rendering of a 3-generation dendrimer: a 3D node
 * graph grown from a central core, gently auto-rotating with cursor parallax.
 * Nodes are depth-sorted, colored teal → sky → indigo by generation, and the
 * whole thing breathes (subtle radial pulse). No external 3D library.
 * ──────────────────────────────────────────────────────────────────────── */

interface Node {
  x: number; y: number; z: number;   // base position (unit-ish sphere)
  gen: number;                        // generation depth (0 = core)
  parent: number;                     // index of parent node (-1 for root)
  seed: number;                       // per-node phase for the breathing wobble
}

// Generation palette: core → outer shells.
const GEN_COLORS = [
  [45, 212, 191],   // teal-400   (core)
  [20, 184, 166],   // teal-500
  [56, 189, 248],   // sky-400
  [129, 140, 248],  // indigo-400 (outermost)
];

// Fibonacci-sphere direction for the k-th of n points — even spherical spread,
// the same golden-ratio trick the real UDB placement engine uses.
function fibDir(k: number, n: number, jitter: number): [number, number, number] {
  const golden = Math.PI * (3 - Math.sqrt(5));
  const y = 1 - (k / Math.max(1, n - 1)) * 2;     // 1 → -1
  const r = Math.sqrt(Math.max(0, 1 - y * y));
  const theta = golden * k + jitter;
  return [Math.cos(theta) * r, y, Math.sin(theta) * r];
}

function buildDendrimer(): Node[] {
  const nodes: Node[] = [];
  const core: Node = { x: 0, y: 0, z: 0, gen: 0, parent: -1, seed: 0 };
  nodes.push(core);

  const F = 4;          // core arms
  const M = 2;          // branching multiplicity
  const GENS = 3;       // shells
  const shellR = [0, 1.0, 1.85, 2.7];   // radius per generation

  // Generation 1: F arms off the core, spread over the sphere.
  let frontier: number[] = [];
  for (let i = 0; i < F; i++) {
    const [dx, dy, dz] = fibDir(i, F, 0.6);
    const r = shellR[1];
    nodes.push({ x: dx * r, y: dy * r, z: dz * r, gen: 1, parent: 0, seed: Math.random() * 6.28 });
    frontier.push(nodes.length - 1);
  }

  // Generations 2..GENS: each frontier node spawns M children, biased outward
  // from its parent direction so the tree opens up like a real starburst.
  for (let g = 2; g <= GENS; g++) {
    const next: number[] = [];
    const r = shellR[g];
    for (const pIdx of frontier) {
      const p = nodes[pIdx];
      const plen = Math.hypot(p.x, p.y, p.z) || 1;
      const out: [number, number, number] = [p.x / plen, p.y / plen, p.z / plen];
      for (let c = 0; c < M; c++) {
        // perturb the outward direction with a fib-sampled offset
        const [ox, oy, oz] = fibDir(c + pIdx, M + 3, g * 1.3);
        const mix = 0.55;
        let dx = out[0] * (1 - mix) + ox * mix;
        let dy = out[1] * (1 - mix) + oy * mix;
        let dz = out[2] * (1 - mix) + oz * mix;
        const dl = Math.hypot(dx, dy, dz) || 1;
        dx /= dl; dy /= dl; dz /= dl;
        nodes.push({ x: dx * r, y: dy * r, z: dz * r, gen: g, parent: pIdx, seed: Math.random() * 6.28 });
        next.push(nodes.length - 1);
      }
    }
    frontier = next;
  }
  return nodes;
}

export default function DendrimerHero() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const nodes = buildDendrimer();

    // pointer parallax (target + eased current)
    const pointer = { tx: 0, ty: 0, x: 0, y: 0 };
    let dpr = Math.min(window.devicePixelRatio || 1, 2);
    let W = 0, H = 0;

    function resize() {
      const rect = canvas.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = rect.width; H = rect.height;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);

    function onMove(e: PointerEvent) {
      const rect = canvas.getBoundingClientRect();
      pointer.tx = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      pointer.ty = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
    }
    window.addEventListener('pointermove', onMove);

    let raf = 0;
    let t = 0;

    function project(n: Node, ax: number, ay: number, pulse: number) {
      // breathing: nudge each node radially
      const breath = 1 + Math.sin(t * 1.1 + n.seed) * 0.018 + pulse * (n.gen / 3) * 0.05;
      let x = n.x * breath, y = n.y * breath, z = n.z * breath;
      // rotate around Y
      let cx = Math.cos(ay), sx = Math.sin(ay);
      let x1 = x * cx + z * sx;
      let z1 = -x * sx + z * cx;
      // rotate around X
      let cy = Math.cos(ax), sy = Math.sin(ax);
      let y1 = y * cy - z1 * sy;
      let z2 = y * sy + z1 * cy;
      return { x: x1, y: y1, z: z2 };
    }

    function frame() {
      t += reduce ? 0 : 0.006;
      // ease pointer
      pointer.x += (pointer.tx - pointer.x) * 0.05;
      pointer.y += (pointer.ty - pointer.y) * 0.05;

      const ay = t * 0.5 + pointer.x * 0.5;
      const ax = -0.25 + pointer.y * 0.35;
      const pulse = (Math.sin(t * 0.8) + 1) / 2;

      ctx.clearRect(0, 0, W, H);

      const cx = W / 2;
      const cy = H / 2;
      const scale = Math.min(W, H) * 0.165;

      // project all
      const pts = nodes.map(n => project(n, ax, ay, pulse));

      // perspective + screen coords (depth used for size/alpha)
      const screen = pts.map(p => {
        const persp = 1 / (1 + (p.z + 3) * 0.06);
        return {
          sx: cx + p.x * scale * persp,
          sy: cy + p.y * scale * persp,
          depth: p.z,
          persp,
        };
      });

      // ── bonds (draw first, behind nodes) ──
      for (let i = 1; i < nodes.length; i++) {
        const a = screen[nodes[i].parent];
        const b = screen[i];
        const avgDepth = (a.depth + b.depth) / 2;
        const dn = (avgDepth + 3) / 6;                 // ~0..1 normalized depth
        const alpha = 0.12 + (1 - dn) * 0.5;
        const col = GEN_COLORS[Math.min(nodes[i].gen, 3)];
        ctx.strokeStyle = `rgba(${col[0]},${col[1]},${col[2]},${alpha.toFixed(3)})`;
        ctx.lineWidth = 0.6 + (1 - dn) * 1.4;
        ctx.beginPath();
        ctx.moveTo(a.sx, a.sy);
        ctx.lineTo(b.sx, b.sy);
        ctx.stroke();
      }

      // ── nodes (depth-sorted back→front) ──
      const order = nodes.map((_, i) => i).sort((p, q) => screen[p].depth - screen[q].depth);
      for (const i of order) {
        const s = screen[i];
        const n = nodes[i];
        const dn = (s.depth + 3) / 6;
        const col = GEN_COLORS[Math.min(n.gen, 3)];
        const baseR = n.gen === 0 ? 9 : 4.6 - n.gen * 0.6;
        const r = Math.max(1.2, baseR * s.persp);
        const alpha = 0.45 + (1 - dn) * 0.55;

        // glow
        const grad = ctx.createRadialGradient(s.sx, s.sy, 0, s.sx, s.sy, r * 3.2);
        grad.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${(alpha * 0.55).toFixed(3)})`);
        grad.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`);
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(s.sx, s.sy, r * 3.2, 0, Math.PI * 2);
        ctx.fill();

        // core dot
        ctx.fillStyle = `rgba(${col[0]},${col[1]},${col[2]},${alpha.toFixed(3)})`;
        ctx.beginPath();
        ctx.arc(s.sx, s.sy, r, 0, Math.PI * 2);
        ctx.fill();

        // bright highlight on the core node
        if (n.gen === 0) {
          ctx.fillStyle = 'rgba(236,254,255,0.9)';
          ctx.beginPath();
          ctx.arc(s.sx - r * 0.25, s.sy - r * 0.25, r * 0.4, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      window.removeEventListener('pointermove', onMove);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="block w-full h-full"
      aria-label="Interactive 3D dendrimer: a 4-arm core branching through three generations"
      role="img"
    />
  );
}
