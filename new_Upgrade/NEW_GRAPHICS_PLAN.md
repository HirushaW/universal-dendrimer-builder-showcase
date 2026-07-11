# UDB Website — Graphics & UI/UX Master Upgrade Plan

**Codename:** *Fusion HUD — Site-Wide Unification & Living Background*
**Author:** Claude Fable 5 (planning) · for Hirusha Walgampaya
**Date:** 2026-07-11
**Status:** PLAN — no website files modified yet (this document is the gate)
**Scope target:** `/home/hirushawalgampaya/Downloads/udb-website/`

---

## 0. Reading This Document

This is the single source of truth for the upgrade. Nothing in `src/` gets touched
until this plan is reviewed. It is grounded in an audit of the *actual current code*
(not assumptions), so every "modify" item below points at a file that really exists
and a problem that is really there.

Jump map:

- [1. Executive Summary](#1-executive-summary)
- [2. Current-State Audit](#2-current-state-audit-what-is-really-there)
- [3. Design Language / Theme Architecture](#3-design-language--theme-architecture)
- [4. Implementation Roadmap (Phased)](#4-implementation-roadmap-phased)
- [5. Global Theme Unification](#5-global-theme-unification-step-2)
- [6. Divider-Line Removal](#6-divider-line-removal-step-3)
- [7. Top Navigation Redesign](#7-top-navigation-redesign-step-4)
- [8. Animation Architecture](#8-animation-architecture-steps-5-7)
- [9. Living Animated Background](#9-living-animated-background-steps-6-8)
- [10. Performance Strategy](#10-performance-strategy-step-9)
- [11. Responsive Strategy](#11-responsive-strategy-step-10)
- [12. Accessibility](#12-accessibility-step-11)
- [13. Folder Structure](#13-folder-structure)
- [14. Component Disposition Table](#14-component-disposition-reuse--modify--redesign)
- [15. Risk Analysis](#15-risk-analysis)
- [16. Expected Improvements](#16-expected-improvements)
- [17. Verification & Acceptance](#17-verification--acceptance-checklist)

---

## 1. Executive Summary

The home page (`src/pages/index.astro`) already carries the target aesthetic:
**Theme 01 "Fusion HUD · Glass · Glitch"** — deep-space navy, cyan glow, glassmorphic
panels with corner brackets, orbital rings, a live procedural dendrimer reactor canvas,
scanlines, and glitch titles. The user loves it.

**The problem is consistency, not direction.** The audit (§2) shows the theme is only
*partially* propagated: reusable component classes (`.card`, `.btn-*`, `.table-scientific`)
were re-themed globally, so inner-page *content* inherits the HUD look — but eight inner
pages still open with inline `bg-gradient-to-br from-slate-950 …` hero bands, scroll-reveal
animation lives only on the homepage, and the site-wide background is a **static** CSS grid.
An animated background component (`ScienceBackground.astro`) was even built — but it is
imported nowhere.

**This upgrade does five things:**

1. **Unify** — promote the HUD hero treatment to a shared component so all 11 pages open like the homepage.
2. **Declutter** — remove decorative divider/dash lines site-wide; replace with whitespace + alignment.
3. **Elevate the top nav** — turn the easy-to-miss hover dropdown into a bold, visible, animated command panel.
4. **Bring the background to life** — a multi-layer, scroll-reactive scientific canvas (dendrimers, DNA, molecular graph, data/particles, equations) behind every page, throttled and capability-gated so it never costs readability or frame budget.
5. **Make motion universal + smooth + accessible** — one shared animation layer (reveal, parallax, hover) tuned per device tier and fully honoring `prefers-reduced-motion`.

**Non-negotiables:** the homepage's current look is *preserved*, not replaced. Performance
on mobile must not regress. Readability of scientific content is sacred — the background is
always subordinate.

---

## 2. Current-State Audit (what is really there)

### 2.1 Stack
- Astro 4 static site + Tailwind CSS 3, one React island (`DendrimerCalculator.tsx`).
- Global styles: `src/styles/global.css` (486 lines) — base `@layer components` + an appended **Theme 01 HUD layer**.
- Layout shell: `src/layouts/Layout.astro` — imports global CSS, renders `Nav` + `<main>` + `Footer`. Body background hard-set `#04070e`.

### 2.2 The 11 pages
| # | Route | File | Hero today |
|---|-------|------|-----------|
| 1 | `/` | `pages/index.astro` | ✅ Full HUD (reactor, telemetry) |
| 2 | `/tools/udb/` | `tools/udb/index.astro` | ⚠️ inline slate gradient |
| 3 | `/tools/udb/install/` | `.../install/index.astro` | ⚠️ inline slate gradient |
| 4 | `/tools/udb/manual/` | `.../manual/index.astro` | ⚠️ inline slate gradient |
| 5 | `/tools/udb/examples/` | `.../examples/index.astro` | ⚠️ inline slate gradient |
| 6 | `/tools/udb/structures/` | `.../structures/index.astro` | gallery |
| 7 | `/tools/udb/structures/[type]/` | `.../structures/[type].astro` | live MOL2 viewer + divider |
| 8 | `/tools/udb/validation/` | `.../validation/index.astro` | ⚠️ inline slate gradient + white-bg charts |
| 9 | `/tools/udb/changelog/` | `.../changelog/index.astro` | ⚠️ inline slate gradient |
| 10 | `/docs/` | `pages/docs/index.astro` | ⚠️ inline slate gradient |
| 11 | `/about/` | `pages/about/index.astro` | ⚠️ inline slate gradient (Profile) |

*(Contact / Publications from the user's brief do not yet exist as pages — treated as optional Phase 5 additions, see §4.)*

### 2.3 Confirmed gaps (the real to-do list)
- **G1 — Inconsistent heroes.** 8 pages open with `from-slate-9xx` inline gradients → visually flatter than the homepage. *(grep-confirmed.)*
- **G2 — Motion is homepage-only.** `.reveal` / `.reveal-group` IntersectionObserver wiring exists **only** in `index.astro`. Inner pages load flat, no progressive appearance.
- **G3 — Background is static.** Atmosphere is `body::before` (radial glows) + `body::after` (grid). No motion. `ScienceBackground.astro` (a working animated molecular-network canvas) is **imported nowhere** — orphaned.
- **G4 — Divider clutter.** `.section-rule`, `.hud-divider`, `<hr>` appear in `index.astro`, `Footer.astro`, `structures/[type].astro`; the base CSS also styles `.section-rule` as a glowing rule. User wants these gone.
- **G5 — Top nav under-reads.** Primary tabs are small text+icon; the "Builder" module list is a **hover-only dropdown** (`opacity-0 invisible group-hover:*`) — invisible until hovered, unusable as a wayfinding panel, and touch-hostile on tablets.
- **G6 — Reactor is single-use.** The signature `DendrimerReactor` canvas only appears on the homepage.

### 2.4 What is already good (preserve, do not rebuild)
- The Theme 01 HUD CSS layer (vars, `.hud-panel`, `.hud-corners`, `.glitch`, `.orbit`, `.hud-btn`, `.hud-chip`, `.hud-eyebrow`, `.hud-terminal`, scanlines).
- Re-themed base classes (`.card`, `.btn-primary/outline`, `.table-scientific`, `.code-block`, `.diagram-frame`, `.structure-frame`) → inner-page **content** already looks HUD.
- `DendrimerReactor.astro` (procedural PAMAM build/collapse loop, reduced-motion aware).
- `.reveal` system + `prefers-reduced-motion` block already in `global.css` (lines ~459–486). We *extend* these, not reinvent.

---

## 3. Design Language / Theme Architecture

### 3.1 Tokens (locked — already in `:root`, do not change values)
```
--hud-cy        #2ce8d8   cyan (primary line/glow)
--hud-cy-bright #6ffff2   bright cyan (accents, active)
--hud-cy-deep   #0e8b86   muted cyan (labels)
--hud-mag       #ff3b8b   magenta (glitch channel only — sparingly)
--hud-ink       #04070e   deep-space navy (page bg)
--hud-ink-2     #071018   panel ink
--hud-line      rgba(44,232,216,0.16)   hairline borders
--hud-line-soft rgba(44,232,216,0.08)   grid / faint
--hud-glass     rgba(8,20,28,0.55)      glass fill
```
Fonts (locked): **Chakra Petch** (display), **Orbitron** (HUD numerics), **JetBrains Mono**
(terminal/labels), **Inter** (body). *Note:* `Layout.astro` currently only preloads Inter +
JetBrains Mono via `<link>`; `global.css` `@import`s all four. Consolidate to one path
(see §10.4) so Chakra Petch / Orbitron load reliably above the fold.

### 3.2 New shared tokens to add (additive, non-breaking)
```
--hud-radius        14px         standard panel radius
--ease-hud          cubic-bezier(.2,.7,.2,1)   the house easing (already used ad-hoc)
--dur-fast 200ms  --dur-med 350ms  --dur-slow 800ms
--bg-veil           rgba(4,7,14,0.55)   scrim used to protect text over the live bg
```

### 3.3 Layering model (z-index contract — prevents the "background eats content" risk)
```
 z -3   body background color                (#04070e)
 z -2   body::before radial glows            (static ambience, kept)
 z -1   <ScienceCanvas> living background     (NEW — animated, pointer-events:none)
 z  0   body::after grid (re-tuned, optional) 
 z  1   page content / <main>
 z 40   local hud-scan sweeps, orbit dots (inside panels)
 z 50   sticky Nav
```
The living background sits at `z:-1`, **always** `pointer-events:none`, and every text
surface that overlaps it gets a `--bg-veil` scrim. This is the single most important
structural rule of the whole upgrade.

---

## 4. Implementation Roadmap (Phased)

Each phase is independently shippable and buildable (`npm run build` must pass at every
phase boundary). Order is chosen so risk is front-loaded into isolated, reversible commits.

**Phase 0 — Scaffolding & tokens** *(no visible change)*
- Add new CSS tokens (§3.2), the `--bg-veil` scrim util, and a `.page-hero` shared class.
- Create `src/components/ScienceCanvas.astro` (the new living background) — but **not** yet mounted.
- Create `src/components/PageHero.astro` and `src/components/RevealInit.astro` (shared scroll-reveal script).

**Phase 1 — Motion + reveal go global** *(low risk)*
- Move the IntersectionObserver reveal script out of `index.astro` into `RevealInit.astro`, mount it once in `Layout.astro`. Every page gains progressive appearance for free.
- Add global smooth-scroll polish + honor reduced-motion (already partly present).

**Phase 2 — Living background** *(medium risk, isolated)*
- Mount `ScienceCanvas` in `Layout.astro` at `z:-1`. Retire/absorb the orphan `ScienceBackground.astro`.
- Ship with capability gating + reduced-motion static frame from day one.

**Phase 3 — Global theme unification** *(the big visual win)*
- Introduce `PageHero.astro`; replace the 8 inline slate hero bands with it.
- Optionally drop a compact `DendrimerReactor` (`compact` prop) into select page heroes.
- Apply `.reveal` groupings to inner-page sections.

**Phase 4 — Nav redesign + divider purge** *(polish)*
- Redesign top nav (§7): visible command panel, better cards/hover/glow, tablet-friendly.
- Remove all decorative dividers (§6).

**Phase 5 — Optional new pages + chart re-skin** *(stretch)*
- Add Publications / Contact pages if desired (brief mentioned them; they don't exist yet).
- Regenerate validation charts with transparent/dark backgrounds (removes the white-box contrast noted in memory).

**Phase 6 — QA pass** — device matrix, Lighthouse, reduced-motion, keyboard, ship.

---

## 5. Global Theme Unification (Step 2)

**Goal:** all 11 pages feel like one application.

**Mechanism — a shared `PageHero.astro`:**
```
Props: eyebrow, title, subtitle, glitch?(bool), reactor?(bool|compact), breadcrumb?, actions?(slot)
Renders: .page-hero band using HUD tokens (NOT slate), hud-eyebrow, glitch-capable
         hud-title, optional orbital rings, optional compact reactor, corner brackets.
```
Then, per page, replace:
```diff
- <section class="bg-gradient-to-br from-slate-950 to-slate-900 …"> … hand-rolled hero … </section>
+ <PageHero eyebrow="// USER MANUAL" title="User Manual" subtitle="…" glitch />
```
**Applies to:** pages #2,3,4,5,8,9,10,11 (the 8 slate heroes). Gallery (#6) and viewer (#7)
get a lighter `PageHero` variant that doesn't fight their existing media.

**Unified surface checklist (must hold on every page):**
- Background: inherits living canvas + `#04070e` (no local slate gradients).
- Panels: `.hud-panel` / `.card` (already global).
- Buttons: `.hud-btn` / `.btn-primary|outline` (already global).
- Tables: `.table-scientific` (already global).
- Section intros: `.hud-eyebrow` + `.hud-title` (standardize; some pages use plain `.section-title`).
- Motion: `.reveal` on major sections (Phase 1 makes this global).

**Result:** zero bespoke per-page color systems; everything routes through tokens + shared components.

---

## 6. Divider-Line Removal (Step 3)

**Target elements:**
- `.section-rule` (base CSS, glowing top-border) — used in `index.astro`.
- `.hud-divider` (gradient hairline) — used in `index.astro`.
- `<hr>` / bottom-border divs in `Footer.astro`, `structures/[type].astro`.
- Incidental `border-t`/`border-b` used purely as decoration (audit each; **keep** borders that are structural, e.g. table cell rules, panel edges, nav bar bottom).

**Method:** replace divider elements with **rhythm via spacing** — increase vertical
section padding (`py-16 → py-20/24`), lead sections with a `.hud-eyebrow` label (which
already carries a short accent tick), and let the living background + panel edges do the
separating. Net effect: cleaner, more "designed", less busy.

**Guardrail:** removing a divider must never make two sections visually merge. Where a
seam is genuinely needed, use whitespace first; if still ambiguous, a *single* faint
`--hud-line-soft` accent tied to a label — never a full-width glowing bar.

---

## 7. Top Navigation Redesign (Step 4)

**Problem (G5):** primary tabs are small; the Builder module list is a hover-only
`opacity-0 invisible` dropdown — invisible, and dead on touch devices.

**Redesign — "Command Panel" mega-menu:**
- **Primary bar:** keep the 5 icon tabs but enlarge hit area, add an animated active
  underline that *slides* between tabs (shared-element transition), stronger hover glow,
  and a subtle corner-bracket flourish on hover.
- **Builder → full mega-panel:** replace the tiny dropdown with a wide glass panel
  (`.hud-panel hud-corners`) containing **cards** for each module (Overview, Install,
  Manual, Examples, Gallery, Benchmarks, Changelog): each card = icon + label + one-line
  descriptor + hover glow + `translateY` lift. Opens on hover **and** on click/focus
  (keyboard + touch), with a small entrance animation (fade + 6px rise, 180ms).
- **Visibility fixes:** raise contrast of inactive tabs (`slate-400 → slate-300`), add a
  faint always-on hairline under the active tab, ensure the panel has a solid `--bg-veil`
  backing so it reads over the animated background.
- **Mobile:** the existing hamburger drawer is kept but restyled to match (cards, not bare
  links), with the same module descriptors.
- **Accessibility:** `aria-expanded`, `aria-controls`, roving focus, `Esc` to close,
  focus-visible rings. Panel dismisses on outside click / route change.

**Files:** `src/components/Nav.astro` (primary rewrite), small CSS additions to the HUD layer.

---

## 8. Animation Architecture (Steps 5–7)

**One shared vocabulary, four primitives** — defined once in `global.css`, used everywhere:

| Primitive | Trigger | Implementation | Budget |
|-----------|---------|----------------|--------|
| **Reveal** | enter viewport | `.reveal`/`.reveal-group` + one global IntersectionObserver | transform+opacity only |
| **Parallax** | scroll | `transform: translate3d` driven by a single throttled rAF scroll loop (not per-element listeners) | GPU compositor |
| **Hover / lift** | pointer | CSS `:hover` transitions on `.card`,`.hud-btn`,nav cards | GPU |
| **Ambient** | always | canvas background + `.orbit-spin`, `.hud-scan`, `cursor-blink` (existing) | capped, pausable |

**Rules that make it "smooth on any device":**
- Animate **only** `transform` and `opacity` (compositor-friendly; no layout/paint thrash).
- All scroll work funnels through **one** `requestAnimationFrame` loop with a dirty flag —
  no `scroll` handler does layout.
- `will-change` applied sparingly and removed after transition.
- Durations from tokens (`--dur-*`); house easing `--ease-hud`.
- Staggered reveals cap at ~6 children (already the pattern) to avoid long cascades.
- **Device tiers** (see §10.3) scale animation richness automatically.

**Smooth scrolling (Step 7):** keep native `scroll-behavior: smooth` (already set); add
optional *soft* parallax on hero/background layers only. No scroll-hijack / heavy smooth-scroll
libraries (they hurt accessibility + mobile). Progressive section appearance = the reveal
primitive, now global.

---

## 9. Living Animated Background (Steps 6 & 8)

**Concept:** a single fixed full-viewport `<canvas>` at `z:-1`, `pointer-events:none`,
rendering a **subtle, slow, multi-domain scientific scene** that gently parallaxes as you
scroll. It replaces "dull" static grid ambience — behind content, never competing with it.

**Layered scene (back → front, each independently capability-gated):**
1. **Deep field** — slow-drifting particles / "atom cloud" with soft glow sprites *(reuse the pre-rendered glow-sprite trick already in `ScienceBackground.astro` — no per-frame gradients).*
2. **Molecular graph** — nodes + proximity bonds (the existing molecular-network effect), tuned sparser.
3. **Signature motifs** (rotating, low-opacity, parallaxed at different depths):
   - **Dendrimer / PAMAM** radial branch structures (ties to the product).
   - **DNA double helix** ribbon (biology).
   - **Carbon ring / hex lattice** drift (chemistry).
   - **Data/vector layer** — faint matrix-style falling glyphs *or* force-vector field arrows (comp-sci / comp-chem), very low alpha.
   - **Occasional floating equation / coordinate-axis glyph** (math), rare, faint.
4. **Scanline + vignette** wash (already themable) to seat it into the HUD look.

**Scroll behavior:** each layer has a depth factor → different parallax speed (already
prototyped in `ScienceBackground.astro`). Motifs also slowly rotate/float independent of
scroll. Everything moves *gently*; target visual motion is "ambient", not "busy".

**Readability protection (hard rules):**
- Global max opacity budget for the whole canvas is low (≈0.10–0.22 depending on layer).
- Content sections that sit over dense areas carry a `--bg-veil` scrim.
- Canvas never renders above `z:-1`; never intercepts pointer/touch.

**Build path:** promote the orphan `ScienceBackground.astro` into a new, layered
`ScienceCanvas.astro`. We keep its proven performance scaffolding:
- node count scales with viewport area, **capped**;
- glow as a pre-rendered sprite (`drawImage`, no per-frame radial gradients);
- pauses on `visibilitychange` (tab hidden);
- DPR capped (≈1.5);
- `prefers-reduced-motion` → render **one static frame**, no rAF.
Then add the motif layers + device-tier gating (§10.3).

**Per-page theming:** motif *mix* can vary subtly by section (e.g. dendrimer-heavy on the
Builder pages, helix/graph on About) via a `variant` prop — same engine, different weights.

---

## 10. Performance Strategy (Step 9)

### 10.1 Rendering budget
- Target **≤ 60 fps desktop, ≥ 30 fps mid mobile**, background CPU main-thread cost < ~2 ms/frame.
- Single canvas, single rAF loop for the background; single rAF for scroll/parallax. No duplicate loops.

### 10.2 Techniques (all mandatory)
- GPU-accelerated CSS: `transform`/`opacity` only for UI motion.
- `requestAnimationFrame` with dirty-flag; passive scroll listeners.
- Pre-rendered sprites for glow; offscreen where supported.
- DPR cap 1.5; node/particle counts scale to viewport area with hard ceilings.
- Pause on tab hidden; throttle when `document.hidden` or when off-screen.
- Lazy-init the 3Dmol MOL2 viewers (already heavy) — don't let bg + viewer run hot together on the gallery/type pages: dial the background down when a WebGL viewer is active.

### 10.3 Device tiers (auto-detected, gate animation richness)
```
tier = f(prefers-reduced-motion, navigator.hardwareConcurrency,
         deviceMemory, coarse-pointer, viewport width, save-data)
 HIGH   desktop/laptop  → all layers, full particle count, parallax
 MED    tablet/large phone → fewer motifs, lower particle count, reduced parallax
 LOW    small/old mobile, save-data, low cores → base gradient + minimal drift
 STATIC prefers-reduced-motion → one static frame, no rAF
```

### 10.4 Asset/load hygiene
- Consolidate font loading (currently split between `Layout.astro <link>` and `global.css @import`) into one non-blocking path with `preconnect` + `display=swap`; preload the 2 above-the-fold families (Chakra Petch, Inter).
- Keep everything self-contained/static (Astro output) — no new runtime deps for animation (hand-written canvas, no three.js) to protect bundle size + first paint.
- Defer the background script (`is:inline` after content, or `client:idle` pattern).

### 10.5 Budgets to hold
- No net Lighthouse Performance regression vs. current build; target ≥ 90 desktop / ≥ 80 mobile.
- Total JS added for animation < ~12 KB gzipped (hand-rolled canvas).

---

## 11. Responsive Strategy (Step 10)

- **Fluid everything:** relative units, flex/grid, `max-width:100%` media; wide tables/code
  already scroll in `overflow-x:auto` — verify each page's wide content is wrapped.
- **Breakpoints:** align to Tailwind (`sm 640 / md 768 / lg 1024 / xl 1280`). Nav switches to
  drawer < `md` (already), mega-panel only ≥ `md`.
- **Hero scaling:** `PageHero` uses clamp-based type sizes; reactor/motifs shrink or drop on narrow screens.
- **Touch:** all hover-only affordances get tap/focus equivalents (esp. the nav panel, G5 fix).
- **Background:** tier system (LOW on small/coarse-pointer) keeps phones smooth.
- **Test matrix:** 360×640 (small phone), 390×844 (modern phone), 768×1024 (tablet),
  1366×768 (laptop), 1920×1080 (desktop), plus landscape phone.

---

## 12. Accessibility (Step 11)

- **`prefers-reduced-motion`:** already handled in CSS; extend to the new canvas (static
  frame) and nav transitions. This is a *first-class* path, not an afterthought.
- **Contrast:** maintain WCAG AA for body text over the animated bg — enforced via
  `--bg-veil` scrims; audit each page with a contrast checker after Phase 2/3.
- **Keyboard:** nav mega-panel fully operable (Tab/Shift-Tab, Enter/Space, Esc, arrow roving);
  visible `:focus-visible` rings site-wide; skip-to-content link in `Layout`.
- **Semantics:** `aria-hidden` on decorative canvas (already set), `aria-expanded`/`controls`
  on nav triggers, landmark roles, alt text on scientific images.
- **Readable fonts:** minimum body size, generous line-height (Inter already comfortable);
  never rely on color alone for meaning.
- **Respect Save-Data / low power:** maps to LOW/STATIC tier.

---

## 13. Folder Structure

```
udb-website/
├── new_Upgrade/
│   ├── NEW_GRAPHICS_PLAN.md          ← THIS FILE
│   └── theme-previews/               ← existing theme mockups (source of truth for look)
├── src/
│   ├── layouts/
│   │   └── Layout.astro              [MODIFY] mount ScienceCanvas + RevealInit, font consolidation, skip-link
│   ├── components/
│   │   ├── Nav.astro                 [REDESIGN] command-panel mega-menu
│   │   ├── Footer.astro              [MODIFY] remove decorative dividers
│   │   ├── ScienceCanvas.astro       [NEW]  layered living background (absorbs ScienceBackground)
│   │   ├── ScienceBackground.astro   [RETIRE] fold into ScienceCanvas, then delete
│   │   ├── PageHero.astro            [NEW]  shared HUD hero (kills 8 slate bands)
│   │   ├── RevealInit.astro          [NEW]  one global IntersectionObserver reveal script
│   │   ├── DendrimerReactor.astro    [REUSE] optional compact variant in page heroes
│   │   ├── Mol2Viewer / MolViewer*   [REUSE] + bg-dimming hook when WebGL active
│   │   └── DendrimerCalculator.tsx   [REUSE]
│   ├── styles/
│   │   └── global.css                [MODIFY] add tokens (§3.2), reveal/parallax primitives, nav panel, remove .section-rule usage sites, veil util
│   └── pages/                        [MODIFY x8 heroes + reveal groupings]
│       ├── index.astro               [MODIFY] remove local reveal script (now global), drop dividers
│       ├── docs/index.astro
│       ├── about/index.astro
│       └── tools/udb/{index,install,manual,examples,validation,changelog}/…
│                                     structures/{index,[type]}.astro
└── (astro.config, tailwind.config, package.json … unchanged)
```

---

## 14. Component Disposition (Reuse / Modify / Redesign)

| Component | Disposition | What happens |
|-----------|-------------|--------------|
| `global.css` HUD layer | **Reuse + extend** | Add tokens, reveal/parallax primitives, nav panel styles, veil util. Do not alter existing token *values*. |
| `DendrimerReactor.astro` | **Reuse** | Add optional use in page heroes via `compact` prop. |
| `Mol2Viewer` / `MolViewer*` | **Reuse** | Add hook to dim background while WebGL viewer active. |
| `DendrimerCalculator.tsx` | **Reuse** | No change (already in HUD panel). |
| `CitationBlock.astro` | **Reuse** | Verify no stray dividers. |
| `.card`, `.btn-*`, `.table-scientific`, `.code-block`, `.diagram-frame`, `.structure-frame` | **Reuse** | Already global HUD; untouched. |
| `Layout.astro` | **Modify** | Mount `ScienceCanvas` + `RevealInit`, font consolidation, skip-link. |
| `Footer.astro` | **Modify** | Remove decorative divider(s); align to spacing rhythm. |
| The 8 slate-hero pages | **Modify** | Swap inline hero band → `<PageHero>`; add `.reveal` groupings. |
| `index.astro` | **Modify** | Remove its local reveal script (now global), drop `.section-rule`/`.hud-divider`. |
| `structures/[type].astro` | **Modify** | Remove divider; keep viewer. |
| `Nav.astro` | **Redesign** | Command-panel mega-menu (§7). |
| `ScienceBackground.astro` | **Redesign→Retire** | Logic absorbed into `ScienceCanvas.astro`, then removed. |
| `PageHero.astro`, `RevealInit.astro`, `ScienceCanvas.astro` | **New** | See §5, §8, §9. |

---

## 15. Risk Analysis

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|-----------|
| R1 | Animated bg hurts readability | Med | High | `z:-1`, low opacity budget, `--bg-veil` scrims, contrast audit gate (§12). |
| R2 | Frame drops on mobile | Med | High | Device tiers (§10.3), capped counts, single rAF, pause-on-hidden, LOW/STATIC fallbacks. |
| R3 | Background + 3Dmol WebGL viewers contend for GPU | Med | Med | Dim/pause bg when a viewer mounts (gallery/type pages). |
| R4 | Nav mega-panel breaks on touch/keyboard | Med | Med | Click+focus open, Esc, roving focus, ARIA; tested on tablet + screen reader. |
| R5 | Divider removal makes sections merge | Low | Med | Spacing rhythm + eyebrow labels; case-by-case review, keep structural borders. |
| R6 | Reduced-motion users still get motion | Low | High | Single guarded path: CSS block + canvas static-frame + JS `matchMedia` gate, tested. |
| R7 | Homepage look accidentally changed | Low | High | Homepage is the reference; visual diff before/after; only remove its dividers + de-dupe reveal script. |
| R8 | Font flash / layout shift from consolidation | Low | Low | `display=swap`, preconnect, preload 2 families; measure CLS. |
| R9 | Scope creep (new Publications/Contact pages) | Med | Low | Isolated to optional Phase 5; core upgrade ships without them. |
| R10 | Build breakage mid-refactor | Low | Med | Phase boundaries each require green `npm run build`; small commits. |

---

## 16. Expected Improvements

**Visual / UX**
- One coherent, premium, "publication-grade" identity across all 11 pages (kills G1).
- A living, on-brand scientific background that makes the site feel alive without distraction (kills G3, uses the already-built canvas that was sitting unused).
- A top nav that is immediately noticeable, self-explanatory, and touch-friendly (kills G5).
- Cleaner layouts via whitespace over rules (kills G4).
- Consistent, smooth motion on every page, not just home (kills G2).

**Engineering**
- Shared components (`PageHero`, `RevealInit`, `ScienceCanvas`) → less duplication, easier future pages.
- Centralized animation primitives → predictable performance, one place to tune.
- No new heavy runtime deps; static Astro output preserved.

**Measurable acceptance targets**
- Lighthouse: Perf ≥ 90 desktop / ≥ 80 mobile; A11y ≥ 95; no CLS regression.
- 60 fps desktop / ≥ 30 fps mid-tier mobile with background active.
- 0 pages with bespoke slate hero gradients remaining.
- 0 decorative divider lines remaining; structural borders intact.
- Full keyboard + reduced-motion + screen-reader pass.

---

## 17. Verification & Acceptance Checklist

Run at every phase boundary and before final sign-off:

- [ ] `npm run build` passes; `npm run dev` served at `http://localhost:4321/` (HTTP, not HTTPS).
- [ ] Headless screenshots via Chromium **without** `--disable-gpu` (that flag adds a spurious cyan line — known issue).
- [ ] All 11 pages visually consistent (side-by-side against homepage reference).
- [ ] No inline `from-slate-9xx` hero bands remain (`grep`).
- [ ] No decorative dividers remain; tables/panels/nav edges intact.
- [ ] Nav mega-panel: hover, click, keyboard, Esc, touch all work; readable over bg.
- [ ] Background: parallax on scroll; pauses on tab-hide; static frame under reduced-motion; LOW tier on throttled mobile emulation.
- [ ] Contrast AA on every page's body text over the background.
- [ ] Device matrix (§11) checked; no horizontal body scroll anywhere.
- [ ] Lighthouse targets (§16) met.
- [ ] Homepage unchanged except divider removal + dedup of reveal script.

---

### Appendix A — Motif inventory for the living background (Step 6/8 palette)
Chemistry: dendrimer/PAMAM branches · carbon/hex rings · atom clouds · molecular lattice ·
bonds · atomic-orbital lobes. Biology: DNA double helix · molecular chains · (light) protein
ribbon. Comp-chem: coordinate axes · force vectors · simulation grid · MD trajectory traces.
Comp-sci: binary/particle drift · matrix data-flow · neural-net edges · faint code fragments.
Math: floating equation glyphs · vector field · graph-theory node clusters.
**All rendered low-alpha, slow, parallaxed, and tier-gated — ambience, never focus.**

### Appendix B — Guiding principle
> *Preserve the homepage the user already loves; propagate it everywhere; make the whole
> thing breathe with a living scientific background — all without ever making the science
> harder to read or the site slower to use.*

*End of plan. No `src/` files were modified in the creation of this document.*
