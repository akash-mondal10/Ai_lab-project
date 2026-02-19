/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkbg: "#0F172A",
        panel: "#1E293B",
        primary: "#7C3AED",
      },
    },
  },
  plugins: [],
}
