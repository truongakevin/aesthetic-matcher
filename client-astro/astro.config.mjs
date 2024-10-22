import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import sitemap from 'astro-sitemap';

export default defineConfig({
  site: 'https://aestheticmatcher.com',
  integrations: [
    react(),
    sitemap(),
  ],
  output: 'static',
});