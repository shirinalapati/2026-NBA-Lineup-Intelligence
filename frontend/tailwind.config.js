/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
        display: ['"Instrument Serif"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        court: {
          950: '#0a0f14',
          900: '#0f1720',
          850: '#131d28',
          800: '#1a2636',
          700: '#243044',
          accent: '#3d9a7a',
          line: '#c9a227',
          muted: '#8b9aad',
        },
      },
      boxShadow: {
        card: '0 4px 24px rgba(0,0,0,0.35)',
      },
    },
  },
  plugins: [],
};
