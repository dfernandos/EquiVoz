/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// GitHub Pages (subcaminho): VITE_BASE=/nome-do-repo/ (com barras, ex.: /PythonExampleProject/)
const base = (() => {
  const b = (process.env.VITE_BASE || '/').trim()
  if (b === '/' || b === '') return '/'
  return b.endsWith('/') ? b : `${b}/`
})()

export default defineConfig({
  base,
  esbuild: {
    jsx: 'automatic',
  },
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.js',
  },
})
