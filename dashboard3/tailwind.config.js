/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0a0f1c',
        panel: '#0f172a',
        accent: '#21d4fd',
        accent2: '#b721ff',
        pipe: '#9fb3c8',
        pipeEdge: '#6b7280',
        leak: '#ff5f6d',
      },
      boxShadow: {
        glow: '0 0 24px rgba(33, 212, 253, 0.35)',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'Inter', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
