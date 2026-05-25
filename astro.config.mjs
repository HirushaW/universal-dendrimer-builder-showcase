import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import react from '@astrojs/react';

// For GitHub Pages deployment, set:
//   site: 'https://<your-username>.github.io'
//   base: '/<your-repo-name>'
// For Netlify or custom domain, remove base and set site only.
export default defineConfig({
  integrations: [tailwind(), react()],
  // site: 'https://hirushawalgampaya.github.io',
  // base: '/udb-website',
  markdown: {
    shikiConfig: {
      theme: 'one-dark-pro',
      wrap: true,
    },
  },
});
