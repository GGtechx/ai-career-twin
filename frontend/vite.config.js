import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const apiProxyConfig = {
  target: 'http://127.0.0.1:8000',
  changeOrigin: true,
  bypass: (req) => {
    // If the browser is requesting an HTML page (SPA page load or refresh), serve index.html
    if (req.headers.accept && req.headers.accept.includes('text/html')) {
      return '/index.html';
    }
  }
};

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': apiProxyConfig,
      '/auth': apiProxyConfig,
      '/profile': apiProxyConfig,
      '/resume': apiProxyConfig,
      '/companies': apiProxyConfig,
      '/jobs': apiProxyConfig,
      '/skill-gap': apiProxyConfig,
      '/placement': apiProxyConfig,
      '/recommendations': apiProxyConfig,
      '/roadmap': apiProxyConfig,
      '/ai': apiProxyConfig,
      '/twin': apiProxyConfig,
      '/dashboard': apiProxyConfig,
      '/career-target': apiProxyConfig
    }
  }
});
