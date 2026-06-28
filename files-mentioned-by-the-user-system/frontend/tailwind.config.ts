import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        board: "#496a4f",
        brass: "#c49a3f",
        paper: "#f7f5ef",
      },
    },
  },
  plugins: [],
};

export default config;
