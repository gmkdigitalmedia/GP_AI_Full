/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0e1117',
        'dark-card': '#1a1a1a',
        'dark-border': '#333',
        'cyan-primary': '#00d4ff',
        'cyan-secondary': '#00b4d8',
      }
    },
  },
  plugins: [],
}