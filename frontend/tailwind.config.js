/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        dark: {
          900: "#0a0a0c",
          800: "#121217",
          700: "#1c1c24",
        },
        primary: {
          DEFAULT: "#3b82f6",
          dark: "#2563eb",
        },
        accent: {
          DEFAULT: "#10b981",
          danger: "#ef4444",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
