# Universal Dendrimer Builder — Website

Static website for the [Universal Dendrimer Builder (UDB)](/) project.

Built with [Astro](https://astro.build), [Tailwind CSS](https://tailwindcss.com),
and React for interactive components. Deployable to GitHub Pages or Netlify.

---

## Prerequisites

- Node.js 18 or 20
- npm 8+

---

## Run Locally

```bash
# 1. Install dependencies
npm install

# 2. Start the dev server
npm run dev
```

The site will be available at `http://localhost:4321`.

---

## Build for Production

```bash
npm run build
```

Output goes to `./dist/`. Preview the production build locally:

```bash
npm run preview
```

---

## Deploy to GitHub Pages

### Automatic (recommended)

1. Push this repository to GitHub.
2. In your repo → **Settings → Pages**, set Source to **GitHub Actions**.
3. Push to the `main` branch — the workflow in `.github/workflows/deploy.yml` will
   build and deploy automatically.

The workflow passes `--site` and `--base` flags at build time based on the Pages
URL, so `astro.config.mjs` does not need to be modified.

### Manual base path configuration

If you need a custom base path (e.g., for a project page at
`https://username.github.io/repo-name/`), uncomment and edit these lines in
`astro.config.mjs`:

```js
site: 'https://yourusername.github.io',
base: '/your-repo-name',
```

---

## Deploy to Netlify

1. Connect your GitHub repo in the Netlify dashboard.
2. Set Build command: `npm run build`
3. Set Publish directory: `dist`
4. No `base` path needed — leave `astro.config.mjs` as-is.

For a custom domain, set it in Netlify's domain management panel and update
`site:` in `astro.config.mjs` to match.

---

## Project Structure

```
udb-website/
├── public/
│   ├── favicon.svg
│   └── images/
│       ├── dendrimer-hero.svg      ← Replace with actual PAMAM render
│       └── placeholder-gui.svg     ← Replace with real screenshot
├── src/
│   ├── components/
│   │   ├── Nav.astro
│   │   ├── Footer.astro
│   │   ├── CitationBlock.astro
│   │   └── DendrimerCalculator.tsx ← React island (live calculator)
│   ├── layouts/
│   │   └── Layout.astro            ← Base HTML wrapper
│   ├── pages/
│   │   ├── index.astro             ← Landing page (/)
│   │   ├── about/index.astro       ← /about/
│   │   ├── docs/index.astro        ← /docs/
│   │   └── tools/udb/
│   │       ├── index.astro         ← /tools/udb/
│   │       ├── install/index.astro ← /tools/udb/install/
│   │       ├── manual/index.astro  ← /tools/udb/manual/
│   │       ├── examples/index.astro
│   │       ├── validation/index.astro
│   │       ├── limitations/index.astro
│   │       └── changelog/index.astro
│   └── styles/
│       └── global.css
├── astro.config.mjs
├── tailwind.config.mjs
├── tsconfig.json
└── package.json
```

---

## Adding Real Content

Replace these placeholders as the project matures:

| Placeholder | Location | Replace with |
|---|---|---|
| `dendrimer-hero.svg` | `public/images/` | VMD/PyMOL render of PAMAM G3 |
| `placeholder-gui.svg` | `public/images/` | Real UDB screenshot |
| Citation BibTeX | `src/components/CitationBlock.astro` | Actual paper BibTeX |
| Author email | `src/pages/about/index.astro` | Real email |
| ORCID | `src/pages/about/index.astro` | Real ORCID iD |
| GitHub URL | `src/components/Nav.astro`, `Footer.astro` | Real repo URL |
| Theory diagrams | `src/pages/tools/udb/manual/index.astro` | SVG/PNG diagrams |
| Example screenshots | `src/pages/tools/udb/examples/index.astro` | Real screenshots |

---

## Phase Roadmap

| Phase | Status | Content |
|---|---|---|
| Phase 1 | ✅ Complete | Landing, Install, Manual, Citation block |
| Phase 2 | 🔲 Scaffolded | Examples, dendrimer type matrix, tutorial videos |
| Phase 3 | ✅ Complete | Benchmarks, Limitations, Theory section (diagram placeholders) |
| Phase 4 | ✅ Complete | Changelog, Live calculator widget |

---

## Tech Stack

- **Astro 4.x** — static site generator, zero-JS by default
- **Tailwind CSS 3.x** — utility-first styling
- **React 18** — used only for the interactive calculator island
- **@tailwindcss/typography** — prose styling for documentation pages
- **Shiki** (via Astro) — syntax highlighting for code blocks

---

## License

Website source: to be determined. UDB software license: to be determined.
