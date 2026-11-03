import { defineConfig } from 'vite';
import { videoExportPlugin } from './tools/video-export-server.js';

export default defineConfig({
  // Keep the exported study usable beneath any static-host directory.
  base: './',
  plugins: [videoExportPlugin()],
});
