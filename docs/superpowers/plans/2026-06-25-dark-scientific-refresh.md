# UDB Website "Dark Scientific" Refresh — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Swap the UDB website's design system to "Dark Scientific" — Crimson Pro + Atkinson Hyperlegible type and a sky+emerald accent migrated from teal — then audit/fix front-end quality, with page structure and copy unchanged.

**Architecture:** Token-first. Change fonts + accent in `tailwind.config.mjs` and `src/styles/global.css` so shared component classes shift automatically; then a scripted `teal-*`→`sky-*` utility-class sweep across 21 files, followed by targeted emerald for CTA/positive elements; then a checklist-driven audit pass.

**Tech Stack:** Astro 4, Tailwind CSS, React (islands), TypeScript. Build: `npm run build`. No unit-test framework — **the test cycle for each task is `npm run build` (must succeed) + a grep assertion + a visual spot-check.**

## Global Constraints

- **Dark theme only** — keep `slate-950`/`navy-*` backgrounds and glow effects. No light mode.
- **No structure/copy/IA changes** — only tokens and styling. Routes, sections, and text stay.
- **Keep `JetBrains Mono`** for code/formulas/numeric stats; do not migrate mono.
- **Accent mapping (apply verbatim):**
  | Old (teal) | New |
  |---|---|
  | `#14b8a6` / `teal-500` / `rgb(20,184,166)` | sky-500 `#0ea5e9` / `rgb(14,165,233)` |
  | `#2dd4bf` / `teal-400` / `rgb(45,212,191)` | sky-400 `#38bdf8` / `rgb(56,189,248)` |
  | `#5eead4` / `teal-300` | sky-300 `#7dd3fc` |
  | `#818cf8` (indigo gradient stop) | emerald-400 `#34d399` |
  | `teal-*` utility classes (markup) | `sky-*` (same shade) |
- **Emerald is reserved** for CTA / success / positive-data elements (see Task 5), not the blanket primary accent.
- **WCAG AA (4.5:1)** text/UI contrast on dark must hold after migration (verified Task 6).
- Work on branch `redesign/dark-scientific`, **not `main`**. Commit after each task.
- Run Python with `C:\Users\hiruw\miniconda3\python.exe` (the `python3`/`python` on PATH is the broken Store stub).

---

### Task 0: Branch + ignore companion files

**Files:**
- Modify: `.gitignore` (append one line)

- [ ] **Step 1: Create the feature branch off main**

Run:
```bash
cd "C:/Users/hiruw/Desktop/Research/udb_website"
git checkout -b redesign/dark-scientific
```
Expected: `Switched to a new branch 'redesign/dark-scientific'`

- [ ] **Step 2: Ignore the brainstorm companion dir**

Add this line to `.gitignore` (below the existing `.claude/` line):
```
.superpowers/
```

- [ ] **Step 3: Verify it's ignored**

Run: `git status --short`
Expected: `.superpowers/` does NOT appear; `.gitignore` and `docs/superpowers/` (specs/plans) do.

- [ ] **Step 4: Commit**

```bash
git add .gitignore docs/superpowers
git commit -m "chore: branch for dark-scientific refresh; ignore .superpowers companion"
```

---

### Task 1: Typography — fonts in tokens

**Files:**
- Modify: `src/styles/global.css:1` (the `@import`) and `:18-21` (body font)
- Modify: `tailwind.config.mjs:18-21` (`fontFamily`)

**Interfaces:**
- Produces: Tailwind families `font-serif` (Crimson Pro), `font-sans` (Atkinson Hyperlegible), `font-mono` (JetBrains Mono, unchanged) — consumed by Task 4/5 markup.

- [ ] **Step 1: Replace the Google Fonts import (line 1 of `global.css`)**

```css
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Crimson+Pro:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
```

- [ ] **Step 2: Set the body font (`global.css`, the `body` rule)**

Change `font-family: 'Inter', sans-serif;` to:
```css
font-family: 'Atkinson Hyperlegible', system-ui, sans-serif;
```

- [ ] **Step 3: Update `fontFamily` in `tailwind.config.mjs`**

Replace the `fontFamily` block with:
```js
fontFamily: {
  sans: ['Atkinson Hyperlegible', 'system-ui', 'sans-serif'],
  serif: ['Crimson Pro', 'Georgia', 'serif'],
  mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
},
```

- [ ] **Step 4: Make display headings use the serif (`global.css`, `.section-title`)**

Append `font-serif` to the `@apply` line of `.section-title`:
```css
.section-title {
  @apply font-serif text-3xl sm:text-4xl font-extrabold text-slate-100 tracking-tight leading-tight;
}
```

- [ ] **Step 5: Build + verify**

Run: `npm run build`
Expected: build succeeds. Then `grep -n "Inter" src/styles/global.css` → no matches.

- [ ] **Step 6: Commit**

```bash
git add src/styles/global.css tailwind.config.mjs
git commit -m "feat(type): adopt Crimson Pro + Atkinson Hyperlegible, keep mono"
```

---

### Task 2: Core color tokens in `global.css`

Migrate every hardcoded teal value in `global.css` per the Global Constraints mapping. This file holds the accent vars, gradients, buttons, cards, scrollbar, and motion glows.

**Files:**
- Modify: `src/styles/global.css` (lines ~9-13, 23, 37, 50-51, 56, 67, 69-70, 73, 80-81, 84, 88, 116, 121, 133, 140, 147, 153-154, 160, 169, 207, 244, 256, 270-271, 288-305)

- [ ] **Step 1: Rename + repoint the accent vars (`:root`, lines 9-13)**

```css
:root {
  --accent: #0ea5e9;
  --accent-light: #38bdf8;
  --accent-dim: rgba(14,165,233,0.12);
  --glow-accent: 0 0 40px rgba(14,165,233,0.18), 0 0 80px rgba(14,165,233,0.08);
  --glow-accent-sm: 0 0 20px rgba(14,165,233,0.25);
}
```

- [ ] **Step 2: Find any consumers of the old var names**

Run: `grep -rn "var(--teal\|var(--glow-teal" src`
For each hit, replace `--teal`→`--accent`, `--teal-light`→`--accent-light`, `--teal-dim`→`--accent-dim`, `--glow-teal`→`--glow-accent`, `--glow-teal-sm`→`--glow-accent-sm`. (If no hits, nothing to do.)

- [ ] **Step 3: Migrate `::selection`, gradients, buttons, cards, table, dividers, glows, scrollbar (lines 23-169)**

Apply the mapping. Key replacements:
```css
/* line 23 */ ::selection { @apply bg-sky-500/30 text-sky-200; }
/* line 37 gradient-text */ background-image: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 45%, #34d399 100%);
/* line 50 card hover */ @apply border-sky-500/40;
/* line 51 */ box-shadow: 0 0 0 1px rgba(14,165,233,0.15), 0 8px 32px rgba(0,0,0,0.4), 0 0 24px rgba(14,165,233,0.08);
/* line 56 card-accent */ @apply card border-l-2 border-l-emerald-500;   /* emerald: positive accent */
/* line 67 btn focus ring */ focus:ring-sky-500
/* line 69 btn-primary bg */ background: linear-gradient(135deg, #10b981, #0ea5e9);   /* emerald→sky CTA */
/* line 70 */ box-shadow: 0 4px 15px rgba(16,185,129,0.35);
/* line 73 */ box-shadow: 0 6px 24px rgba(16,185,129,0.5);
/* line 80-81 btn-outline hover */ hover:border-sky-500 hover:text-sky-400
/* line 84 */ .btn-outline:hover { box-shadow: 0 0 16px rgba(14,165,233,0.12); }
/* line 88 nav-link */ @apply text-slate-400 hover:text-sky-400 ...;
/* line 116 table row hover */ tr:hover td { @apply bg-sky-500/5; }
/* line 121 section-rule */ box-shadow: 0 -1px 0 rgba(14,165,233,0.06);
/* line 133 diagram-frame */ box-shadow: 0 0 0 1px rgba(14,165,233,0.08), 0 24px 48px rgba(0,0,0,0.5);
/* line 140 structure-frame */ box-shadow: 0 0 40px rgba(14,165,233,0.12), 0 24px 48px rgba(0,0,0,0.6);
/* line 147 glow-orb */ background: radial-gradient(circle, rgba(14,165,233,0.18) 0%, transparent 70%);
/* lines 153-154 grid-bg */ rgba(14,165,233,0.06)   (both gradient lines)
/* line 160 dot-bg */ radial-gradient(rgba(14,165,233,0.15) 1px, transparent 1px);
/* line 169 scrollbar thumb hover */ background: #0ea5e9;
```

- [ ] **Step 4: Migrate the motion block (lines 200-306)**

```css
/* line 207 gradient-text-anim */ background-image: linear-gradient(110deg, #7dd3fc 0%, #38bdf8 35%, #34d399 70%, #7dd3fc 100%);
/* line 244 aurora conic */ background: conic-gradient(from 0deg, rgba(14,165,233,0.16), rgba(56,189,248,0.10), rgba(52,211,153,0.14), rgba(14,165,233,0.16));
/* line 256 card-sheen::before */ background: linear-gradient(90deg, transparent, rgba(56,189,248,0.5), transparent);
/* line 270 scroll-progress */ background: linear-gradient(90deg, #38bdf8, #0ea5e9 55%, #34d399);
/* line 271 */ box-shadow: 0 0 12px rgba(56,189,248,0.55);
/* line 288 back-to-top color */ color: #38bdf8;
/* line 290 */ border: 1px solid rgba(14,165,233,0.35);
/* line 304 */ border-color: rgba(56,189,248,0.7);
/* line 305 */ box-shadow: 0 0 22px rgba(14,165,233,0.3);
```

- [ ] **Step 5: Verify no teal remains in `global.css`**

Run:
```bash
grep -niE "teal|14b8a6|2dd4bf|5eead4|818cf8|rgba\(20,184,166|rgba\(45,212,191" src/styles/global.css
```
Expected: **no matches**. Then `npm run build` → succeeds.

- [ ] **Step 6: Commit**

```bash
git add src/styles/global.css
git commit -m "feat(color): migrate core tokens teal→sky with emerald CTAs"
```

---

### Task 3: tailwind.config color cleanup

**Files:**
- Modify: `tailwind.config.mjs:11-14` (the `teal` color extension)

- [ ] **Step 1: Replace the `teal` brand extension with `accent`**

Replace:
```js
teal: {
  brand: '#0d9488',
},
```
with:
```js
accent: {
  DEFAULT: '#0ea5e9',
  emerald: '#10b981',
},
```

- [ ] **Step 2: Repoint the typography plugin teal links (`tailwind.config.mjs`, `udb` prose block)**

In the `typography` `udb` css, change the two `colors.teal[...]` values:
```js
'--tw-prose-links': theme('colors.sky[400]'),
'--tw-prose-bullets': theme('colors.sky[500]'),
'--tw-prose-quote-borders': theme('colors.sky[500]'),
'--tw-prose-code': theme('colors.sky[300]'),
```

- [ ] **Step 3: Verify + build**

Run: `grep -niE "teal" tailwind.config.mjs` → no matches. Then `npm run build` → succeeds.

- [ ] **Step 4: Commit**

```bash
git add tailwind.config.mjs
git commit -m "feat(color): drop teal from tailwind config; sky prose links"
```

---

### Task 4: Mechanical `teal-*` → `sky-*` sweep across components & pages

The remaining 19 files use `teal-*` Tailwind utility classes in markup. Replace them all with the same `sky-*` shade via a script, then verify.

**Files (all in `src/`):** `components/CitationBlock.astro`, `components/DendrimerCalculator.tsx`, `components/DendrimerHero.tsx`, `components/Footer.astro`, `components/Mol2Viewer.astro`, `components/Nav.astro`, `components/PageHeader.astro`, `data/dendrimers.ts`, `pages/about/index.astro`, `pages/docs/index.astro`, `pages/index.astro`, `pages/tools/udb/changelog/index.astro`, `pages/tools/udb/examples/index.astro`, `pages/tools/udb/index.astro`, `pages/tools/udb/install/index.astro`, `pages/tools/udb/manual/index.astro`, `pages/tools/udb/structures/index.astro`, `pages/tools/udb/structures/[type].astro`, `pages/tools/udb/validation/index.astro`

- [ ] **Step 1: Run the scripted replacement**

This replaces the token `teal-` with `sky-` (covers `text-teal-400`, `bg-teal-500/10`, `border-teal-500`, `ring-teal-500`, `from-teal-400`, `via-teal-300`, etc.) across the listed files only. Run:
```bash
cd "C:/Users/hiruw/Desktop/Research/udb_website"
"C:/Users/hiruw/miniconda3/python.exe" - <<'PY'
import re, pathlib
files = [
 "src/components/CitationBlock.astro","src/components/DendrimerCalculator.tsx",
 "src/components/DendrimerHero.tsx","src/components/Footer.astro",
 "src/components/Mol2Viewer.astro","src/components/Nav.astro",
 "src/components/PageHeader.astro","src/data/dendrimers.ts",
 "src/pages/about/index.astro","src/pages/docs/index.astro","src/pages/index.astro",
 "src/pages/tools/udb/changelog/index.astro","src/pages/tools/udb/examples/index.astro",
 "src/pages/tools/udb/index.astro","src/pages/tools/udb/install/index.astro",
 "src/pages/tools/udb/manual/index.astro","src/pages/tools/udb/structures/index.astro",
 "src/pages/tools/udb/structures/[type].astro","src/pages/tools/udb/validation/index.astro",
]
n=0
for f in files:
    p=pathlib.Path(f); s=p.read_text(encoding="utf-8")
    new=s.replace("teal-","sky-")
    if new!=s: p.write_text(new,encoding="utf-8"); n+=1
print(f"updated {n} files")
PY
```
Expected: `updated N files` (N up to 19).

- [ ] **Step 2: Verify zero `teal-` utility classes remain anywhere**

Run: `grep -rniE "teal-|#14b8a6|#2dd4bf|#5eead4" src`
Expected: **no matches**. (Bare word "teal" in prose copy, if any, is fine — investigate any hit manually; there should be none in class position.)

- [ ] **Step 3: Build + visual spot-check**

Run: `npm run build` → succeeds. Then `npm run dev`, and open Home, `tools/udb/manual`, a per-dendrimer page (`tools/udb/structures/pamam`), and the calculator. Confirm accents render sky-blue, no broken colors.

- [ ] **Step 4: Commit**

```bash
git add src
git commit -m "refactor(color): sweep teal-* utility classes to sky-* across pages/components"
```

---

### Task 5: Targeted emerald for CTA / positive elements

After the blanket sky sweep, re-point genuinely "CTA / success / positive-data" spots to emerald so the palette reads as a blue+green split, not mono-blue.

**Files:** `src/pages/index.astro` (primary hero CTA, stat call-outs), `src/components/DendrimerHero.tsx` (live-data/positive badge), `src/components/DendrimerCalculator.tsx` (success/result highlight), plus any `.btn-primary`/`.card-accent`/`.stat-num` usages found below.

- [ ] **Step 1: Locate candidate spots**

Run:
```bash
grep -rniE "btn-primary|card-accent|stat-num|success|live data|\\bgo\\b|positive" src/pages/index.astro src/components/DendrimerHero.tsx src/components/DendrimerCalculator.tsx
```
Review each hit: if it represents a primary action, a positive/success state, or a headline numeric stat, switch its accent class from `sky-*` to the matching `emerald-*` shade (e.g. `text-sky-400`→`text-emerald-400`, `bg-sky-500/10`→`bg-emerald-500/10`). Leave links, borders, and neutral accents as sky.

- [ ] **Step 2: Apply emerald to the homepage hero stat numbers**

In `src/pages/index.astro`, for the count-up / `stat-num` figures, set the number color to `text-emerald-400` (keep their labels slate). This makes positive data green against the sky-blue UI.

- [ ] **Step 3: Build + visual check**

Run: `npm run build` → succeeds. `npm run dev` → Home hero shows an emerald primary CTA + emerald stat numbers; links/nav remain sky. Confirm the two accents read as intentional, not random.

- [ ] **Step 4: Commit**

```bash
git add src
git commit -m "feat(color): emerald for CTAs and positive-data; sky for links/UI"
```

---

### Task 6: Audit — contrast, focus-visible, cursor-pointer

Run the front-end-design-checklist + ui-ux-pro-max pre-delivery items for interactive states.

**Files:** `src/styles/global.css` (focus + cursor utilities), plus any component with a custom-styled clickable.

- [ ] **Step 1: Contrast check the new accents on dark**

For each accent-on-dark text use (sky-400/300, emerald-400 on slate-950/900), confirm ≥ 4.5:1. sky-400 `#38bdf8` on slate-950 `#020617` ≈ 7.9:1 (pass); emerald-400 `#34d399` on slate-950 ≈ 9.3:1 (pass). For any accent used as *small text on a mid surface* (e.g. on `slate-800`), verify with a contrast tool; if < 4.5:1, bump to the 300 shade. Record results in the commit message.

- [ ] **Step 2: Add a global keyboard focus-visible ring**

In `global.css` `@layer base`, add:
```css
:where(a, button, input, select, textarea, [tabindex]):focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 2px;
  border-radius: 4px;
}
```

- [ ] **Step 3: Ensure clickables show a pointer**

In `global.css` `@layer base`, add:
```css
button, [role="button"], summary, label[for] { cursor: pointer; }
```

- [ ] **Step 4: Build + keyboard test**

Run: `npm run build` → succeeds. `npm run dev`, then Tab through Home: every link/button shows a visible sky focus ring; hovering buttons shows a pointer.

- [ ] **Step 5: Commit**

```bash
git add src/styles/global.css
git commit -m "a11y: focus-visible rings, pointer cursors; verify AA accent contrast"
```

---

### Task 7: Audit — reduced-motion, responsive, 404

**Files:** `src/styles/global.css` (verify reduced-motion), check for `src/pages/404.astro`, create if missing.

- [ ] **Step 1: Confirm reduced-motion already covers the motion system**

Run: `grep -n "prefers-reduced-motion" src/styles/global.css`
Expected: the existing block (lines ~308-312) disables `.reveal`, `.gradient-text-anim`, `.float-y`, `.shimmer`, `.aurora`, `.scroll-progress`, `.back-to-top`. Verify the 3D hero (`DendrimerHero.tsx`) and count-up also respect it:

Run: `grep -rn "prefers-reduced-motion\|matchMedia" src/components/DendrimerHero.tsx src/pages/index.astro`
If the hero/count-up do NOT guard on `matchMedia('(prefers-reduced-motion: reduce)')`, add an early return that renders the static end-state. Show the guard:
```ts
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  // render final frame, skip animation loop
  return;
}
```

- [ ] **Step 2: Responsive spot-check**

`npm run dev`, then at 375px and 768px widths check: Home, `tools/udb/manual` (41 accent uses — densest), a per-dendrimer page, and the calculator. Confirm no horizontal overflow, tables scroll, nav collapses. Fix any overflow with existing responsive utility patterns (`overflow-x-auto`, `sm:`/`md:` prefixes).

- [ ] **Step 3: Ensure a styled 404 exists**

Run: `ls src/pages/404.astro 2>/dev/null || echo MISSING`
If MISSING, create `src/pages/404.astro` using the shared `Layout`:
```astro
---
import Layout from '../layouts/Layout.astro';
---
<Layout title="Page not found" description="That page doesn't exist.">
  <section class="max-w-2xl mx-auto px-6 py-32 text-center">
    <p class="font-mono text-sky-400 text-sm tracking-widest">404</p>
    <h1 class="section-title mt-3">This page wandered off the lattice.</h1>
    <p class="section-subtitle">The page you're looking for doesn't exist or moved.</p>
    <a href="/" class="btn-primary mt-8">Back to home</a>
  </section>
</Layout>
```

- [ ] **Step 4: Build + verify**

Run: `npm run build` → succeeds; confirm `dist/404.html` exists.

- [ ] **Step 5: Commit**

```bash
git add src
git commit -m "a11y/responsive: reduced-motion guards, mobile fixes, styled 404"
```

---

### Task 8: Optional gstack review + final verification

- [ ] **Step 1: gstack design-review (only if installed & working)**

Run: `ls ~/.claude/skills/gstack/browse/dist/browse 2>/dev/null && echo READY || echo SKIP`
If READY and the gstack skills are registered, invoke the gstack design-review / QA skill against the running dev site and triage findings. If SKIP, note "gstack not available — skipped" and continue. **Not a blocker.**

- [ ] **Step 2: Full build + final visual pass**

Run: `npm run build` → succeeds with no warnings about missing assets. Spot-check all page types one more time in `npm run preview`.

- [ ] **Step 3: Confirm zero teal anywhere**

Run: `grep -rniE "teal|14b8a6|2dd4bf|5eead4|818cf8" src tailwind.config.mjs`
Expected: **no matches**.

- [ ] **Step 4: Final commit + push branch**

```bash
git add -A
git commit -m "chore: final dark-scientific refresh verification" --allow-empty
git push -u origin redesign/dark-scientific
```
(Push only if the user wants it pushed; otherwise stop at the commit.)

---

## Self-Review

**Spec coverage:** Type swap → Task 1. Full teal→sky migration → Tasks 2-4. Emerald for CTA/positive → Task 5. Token-first mechanism → Tasks 1-3 before 4. 21-file scope → Tasks 2 (global.css) + 4 (19 files) + 3 (config) = 21. Contrast AA → Task 6. focus-visible/cursor/hover → Task 6. reduced-motion → Task 7. Responsive → Task 7. 404 → Task 7. gstack optional → Task 8. `.gitignore`/branch housekeeping → Task 0. All spec sections covered.

**Placeholder scan:** No "TBD/TODO". Task 5's "candidate spots" are located by an explicit grep + judgement rule (positive/CTA→emerald), not a vague instruction. Each code step shows real code.

**Type/name consistency:** Var rename `--teal*`→`--accent*` defined in Task 2 Step 1, consumers updated Task 2 Step 2. Tailwind `accent` color defined Task 3 used nowhere downstream that conflicts. Font families `font-serif`/`font-sans`/`font-mono` defined Task 1, used Tasks 4-7. Consistent.
