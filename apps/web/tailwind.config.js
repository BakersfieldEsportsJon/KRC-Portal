/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef2f4',
          100: '#fce7eb',
          200: '#f9cfd7',
          300: '#f5a8b7',
          400: '#ef6c88',
          500: '#ec194d',
          600: '#d91545',
          700: '#b6113a',
          800: '#991036',
          900: '#831033',
        }
      }
    },
  },
  plugins: [],
}