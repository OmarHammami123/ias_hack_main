/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:       '#050608',
        surface:  '#0c0e14',
        surface2: '#13161f',
        surface3: '#1a1d28',
        amber:    { 400: '#FBBF24', 500: '#F59E0B', 600: '#D97706' },
        forge:    { 50: '#fdf8ef', 100: '#faecc8', 200: '#f5d690', 300: '#f0bc50', 400: '#FBBF24', 500: '#F59E0B', 600: '#D97706' },
        teal:     { 400: '#2DD4BF', 500: '#14B8A6' },
        coral:    { 400: '#FF8A80', 500: '#FF6B6B', 600: '#EF4444' },
        emerald:  { 400: '#34D399', 500: '#10B981' },
        stone:    { 300: '#d6d3d1', 400: '#a8a29e', 500: '#78716c', 600: '#57534e', 700: '#44403c', 800: '#292524' },
      },
      boxShadow: {
        glow:      '0 0 28px rgba(251,191,36,0.25)',
        'glow-lg': '0 0 48px rgba(251,191,36,0.18)',
        coral:     '0 0 24px rgba(255,107,107,0.35)',
        glass:     '0 4px 30px rgba(0,0,0,0.5)',
        inner:     'inset 0 1px 0 rgba(255,255,255,0.05)',
      },
      fontFamily: {
        display: ['Sora', 'system-ui', 'sans-serif'],
        body:    ['"DM Sans"', 'system-ui', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(rgba(251,191,36,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(251,191,36,0.03) 1px, transparent 1px)',
      },
      backgroundSize: {
        'grid-pattern': '32px 32px',
      },
      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'flow': 'flow 2s linear infinite',
        'shimmer': 'shimmer 2.5s ease-in-out infinite',
      },
      keyframes: {
        flow: {
          '0%':   { strokeDashoffset: '24' },
          '100%': { strokeDashoffset: '0' },
        },
        shimmer: {
          '0%, 100%': { opacity: '0.5' },
          '50%':      { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
