# Changelog

All notable changes to the UDB website are recorded here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) ·
Versioning: [Semantic Versioning](https://semver.org).

## [1.1.0] - 2026-11-14

Motion and polish release.

### Added
- **Page transitions:** moving between pages now crossfades instead of flashing
  (View Transitions API; browsers without it navigate as before).
- **Entrance choreography:** elements that scroll in together cascade in reading
  order; hero headlines rise in line by line; inner-page titles wipe in.
- **Scroll depth:** each page hero recedes (fades and shrinks slightly) as it scrolls
  away, and the home reactor drifts slower than the page. Both use CSS scroll
  timelines, so they run off the main thread.
- **Hover and touch details:** a light traces the rim of a hovered card, icon tiles
  lean in, table rows get a sliding accent bar, footer links underline from the
  left, and menu items cascade in when the Builder menu or mobile drawer opens.
- **Feedback:** in-page jumps briefly highlight their destination; the 3D viewer
  loading state has a soft sweep; the hero title's gradient word shimmers slowly.

### Notes
- Finished animations never override hover states, and the whole layer is off for
  reduced-motion users and trimmed on the low performance tier.

## [1.0.0] - 2026-10-10

First stable release, matching the live site.

### Site
- Pages: Home, UDB Overview, Installation, User Manual, Structure Gallery (one page
  per dendrimer family), Benchmarks, Changelog, Documentation and About.
- Live 3D structure gallery for every family: core, monomer and the full G1–G6
  series, with characterization and build-log data and per-generation provenance
  (AMBER-minimised or as-built).
- Interactive size estimator: terminal groups, atom count, molecular weight and Rg
  from type and generation.

### Design
- Fusion HUD theme with a liquid-glass layer: frosted panels, specular rims,
  pointer-following highlights, a gliding nav indicator and glass controls.
- Professional typography: Space Grotesk (display), Inter (text), JetBrains Mono (data).
- Animated scientific background with a procedural dendrimer "reactor" in the hero.
- Interactions: 3D card tilt, count-up statistics, image lightbox, copy buttons
  on code blocks, Manual scroll-spy, back-to-top.

### Performance
- Adaptive device tiers (`high` / `mid` / `low`) with a frame-rate governor that
  steps down on slow devices and remembers the result for later visits.
- Phones and weak GPUs: live blur kept only on the nav and overlays; the background
  and reactor are capped at 30 fps or held as a still frame. On a phone this cuts
  the GPU layers per page by half (mid) to three-quarters (low): home 155 → 77 / 38.
- 3D viewers: 3Dmol is self-hosted, version-pinned and loaded on demand instead of
  blocking page load. One shared spin scheduler with a render budget replaces a
  separate 40 Hz timer per viewer. Hidden 2× supersampling is off below the high
  tier. Large models (G5/G6) render lighter on weaker tiers. On low-end devices
  models load on tap.
- Image decoding is lazy and asynchronous, the profile photo dropped from 571 KB to
  23 KB, the calculator hydrates on view, and long-lived cache headers apply to
  hashed assets.

### Fixes
- Phone layouts: home hero text overflowed its panel; the Manual page overflowed horizontally.
- Social previews and canonical URLs now point to the real site, and a share image was added.
- Visible keyboard focus on angled buttons; in-page anchors land below the sticky nav.

### Repository
- Removed internal planning notes, unused images, an unused component and the
  non-functional GitHub Pages workflow (the site is deployed on Vercel).
- Branch model: `main` (stable, live) and `dev` (ongoing work).

### License
- Open source under the MIT License, with a security policy (`SECURITY.md`).
