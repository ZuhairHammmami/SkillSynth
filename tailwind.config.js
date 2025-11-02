// المسار: src/frontend/tailwind.config.js

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // -->> ابدأ الإضافة من هنا <<--
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))", // لون الخلفية العام
        foreground: "hsl(var(--foreground))", // لون النص الأساسي
        primary: {
          DEFAULT: "hsl(var(--primary))", // اللون الرئيسي (للأزرار والروابط)
          foreground: "hsl(var(--primary-foreground))", // لون النص فوق اللون الرئيسي
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        // ... يمكنك إضافة ألوان أخرى مثل destructive, muted, accent
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      // -->> انتهت الإضافة <<--
    },
  },
  plugins: [],
};