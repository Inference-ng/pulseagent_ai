import forms from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#0A1628',
        panel: '#10243e',
        ink: '#ffffff',
        mist: '#b6c7db',
        emerald: '#00D4AA',
        amber: '#00D4AA',
        danger: '#f87171',
      },
      boxShadow: {
        glow: '0 24px 80px rgba(16, 185, 129, 0.15)',
      },
      backgroundImage: {
        'hero-grid': 'radial-gradient(circle at top, rgba(16, 185, 129, 0.18), transparent 35%), linear-gradient(135deg, rgba(245, 158, 11, 0.12), transparent 40%), linear-gradient(180deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0))',
      },
    },
  },
  plugins: [forms],
};