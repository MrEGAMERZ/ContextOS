/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: { 50: '#f0fdf4', 500: '#22c55e', 600: '#16a34a' },
        accent: { 500: '#06b6d4', 600: '#0891b2' },
        amazon: { 500: '#ff9900', 600: '#e68a00' },
        bedrock: { 500: '#a855f7', 600: '#9333ea' }
      }
    },
  },
  plugins: [],
}
