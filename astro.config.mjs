import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import react from '@astrojs/react';

export default defineConfig({
  // Production URL (Vercel). Used for canonical links and social-card image URLs.
  site: 'https://universal-dendrimer-builder-showcas.vercel.app',
  integrations: [tailwind(), react()],
  markdown: {
    shikiConfig: {
      theme: 'one-dark-pro',
      wrap: true,
    },
  },
});
