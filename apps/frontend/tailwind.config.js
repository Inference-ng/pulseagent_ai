import forms from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        canvas:  '#060D1A',
        surface: '#0D1B2E',
        panel:   '#0F2340',
        border:  'rgba(255,255,255,0.08)',
        ink:     '#F0F6FF',
        mist:    '#7A9BB5',
        dim:     '#3D5A73',
        // Fixed: emerald and amber are DIFFERENT colours
        emerald: '#00C896',
        amber:   '#F59E0B',
        danger:  '#F87171',
        gold:    '#FFD166',
      },
      boxShadow: {
        glow:    '0 0 0 1px rgba(0,200,150,0.15), 0 8px 32px rgba(0,200,150,0.08)',
        card:    '0 1px 3px rgba(0,0,0,0.4), 0 8px 24px rgba(0,0,0,0.2)',
        amber:   '0 0 0 1px rgba(245,158,11,0.2), 0 4px 16px rgba(245,158,11,0.08)',
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)',
        'hero-glow': 'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,200,150,0.15), transparent)',
        'amber-glow': 'radial-gradient(ellipse 60% 40% at 80% 50%, rgba(245,158,11,0.1), transparent)',
      },
      backgroundSize: {
        'grid': '40px 40px',
      },
      animation: {
        'pulse-dot': 'pulse-dot 2s ease-in-out infinite',
        'fade-up': 'fade-up 0.5s ease-out forwards',
        'typewriter': 'typewriter 0.05s steps(1) infinite',
      },
      keyframes: {
        'pulse-dot': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.4', transform: 'scale(0.85)' },
        },
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [forms],
};
