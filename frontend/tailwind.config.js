/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ["'JetBrains Mono'", "'Fira Code'", "'Cascadia Code'", 'monospace'],
      },
      colors: {
        surface: {
          primary: '#1e1e2e',
          secondary: '#181825',
          tertiary: '#11111b',
        },
        border: '#313244',
        accent: '#f59e0b',
      },
    },
  },
  plugins: [],
};
