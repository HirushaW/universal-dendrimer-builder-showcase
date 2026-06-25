# UDB Website — "Dark Scientific" Refresh + Audit

**Date:** 2026-06-25
**Status:** Approved direction, pending spec review
**Scope:** Visual design-system swap (structure & content unchanged) + a front-end
quality audit/fix pass.

## Goal

Apply a new, cohesive design system to the existing `udb_website` (Astro + Tailwind +
React) — evolving the current dark "lab" aesthetic rather than replacing it — then
audit the restyled site against a front-end checklist and fix the gaps. Page
structure, routes, and copy stay as they are.

Design direction chosen ("Option B — Dark Scientific") via ui-ux-pro-max-generated
candidates: keep the dark base + glow, adopt a scholarly serif/legible type pairing,
and migrate the single teal accent to a blue+green split.

## Non-goals

- No layout/section/IA changes, no new pages, no copy rewrites.
- No content-model or data changes (`src/data/dendrimers.ts` values unchanged; only
  styling tokens it references are migrated).
- No light-mode theme.

## Phase 1 — Design tokens

### Typography
Replace Inter with a two-family system; keep mono for code/data.

| Role | New | Was |
|---|---|---|
| Headings / display | **Crimson Pro** (serif, 400–700) | Inter |
| Body / UI | **Atkinson Hyperlegible** (400/700) | Inter |
| Code / formulas / numeric stats | **JetBrains Mono** (unchanged) | JetBrains Mono |

- Update the Google Fonts `@import` in `src/styles/global.css`.
- Update `fontFamily` in `tailwind.config.mjs`: `sans → Atkinson Hyperlegible`, add
  `serif → Crimson Pro`, `mono` unchanged.
- `.section-title` / display headings use the serif; body defaults to sans.

### Color — stay dark, migrate accent (FULL MIGRATE)
Current state: one teal accent (`#14b8a6` / Tailwind `teal-*`) drives links, borders,
glows, card hovers, and a teal→sky→indigo `.gradient-text`. Teal appears in **21
files (~200 occurrences)**, predominantly as `teal-300/400/500` utility classes.

New accent system:

| Token | New value | Usage |
|---|---|---|
| Primary accent | **sky** `#38bdf8` (`sky-400`) | links, borders, focus rings, default accent |
| Secondary accent | **emerald** `#34d399` (`emerald-400`) | "go"/positive/data-highlight, secondary glow |
| CTA | **emerald** `#10b981` (`emerald-500`) | primary buttons / call-to-action |
| Gradient-text | **sky → emerald** | retire the indigo `#818cf8` stop |
| Base / surfaces | unchanged | `slate-950` / `navy-*` backgrounds, glow effects retained |

**Migration mechanism (decided: full migrate, not var-retune):**
1. **Mechanical sweep:** replace `teal-` → `sky-` across all 21 files (markup +
   components). This makes sky the drop-in primary accent at matching shades.
2. **Targeted emerald:** after the sweep, re-point genuinely "CTA / success / positive"
   elements to emerald — primary buttons, stat call-outs, success states,
   `card-accent` left-border on positive cards. (Identified per-file during
   implementation, not blanket.)
3. **CSS vars + components:** rename/repoint `--teal*`, `--glow-teal*` in `global.css`
   to sky/emerald-based `--accent*` / `--glow*`; update `.gradient-text`, `.card`
   hover, `::selection`.
4. **tailwind.config.mjs:** drop `teal.brand`; if a named brand color is wanted, add
   `accent` (sky) — otherwise rely on Tailwind's stock `sky`/`emerald`.

### Application strategy
Token-first: change `tailwind.config.mjs` + `global.css` so shared component classes
(`.card`, `.section-title`, `.gradient-text`, etc.) shift automatically; then the
mechanical `teal→sky` sweep + targeted emerald handles hard-coded utility classes in
the 21 files. Files touched are exactly those 21 (listed in the implementation plan).

## Phase 2 — Audit & fix

Run the **front-end-design-checklist** skill + ui-ux-pro-max's pre-delivery checklist
against the restyled site; fix gaps found. Checklist:

- **Contrast:** new sky/emerald-on-dark text & UI meets **WCAG AA (4.5:1)**; adjust
  shades up/down if any fail.
- **Interactive states:** `:focus-visible` rings for keyboard nav on all links/buttons/
  inputs; `cursor-pointer` on clickables; hover transitions 150–300ms.
- **Motion:** wrap heavy motion (3D hero, scroll-reveal, count-up) so
  `prefers-reduced-motion: reduce` disables/limits it.
- **Responsive:** mobile + tablet pass on each page type (home, docs, tool subpages,
  per-dendrimer, calculator).
- **Assets/pages:** confirm a styled **404 page** exists (add if missing); favicon
  present; no emoji-as-icons.
- **gstack design-review / QA-in-browser:** run **only if** gstack finishes installing
  and is confirmed working; otherwise skipped (not a blocker).

## Risks & mitigations
- **Wide blast radius (21 files):** mechanical sweep risks over-replacing (e.g., a
  `teal` that was intentionally distinct). Mitigation: review the sweep diff per file;
  build + visually spot-check key pages before commit.
- **Contrast regressions:** sky/emerald on `slate-950` differs from teal; verify AA in
  Phase 2 rather than assuming.
- **Branch hygiene:** currently on `main`. Do the work on a feature branch
  (`redesign/dark-scientific` or existing `dev`), not `main`.

## Housekeeping
- Add `.superpowers/` to `.gitignore` (currently only `.claude/` is ignored) so the
  brainstorm companion files aren't committed.

## Verification
- `npm run build` succeeds.
- Visual spot-check of home, a tool subpage, a per-dendrimer page, and the calculator.
- Phase-2 checklist items pass (contrast, focus, reduced-motion, responsive, 404).
