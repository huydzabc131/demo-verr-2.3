/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#18181B',
        cardBg: '#27272A',
        accentBlue: '#2563EB',
        hoverBlue: '#1D4ED8',
      }
    },
  },
  plugins: [],
}
