/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        corporate: {
          blue: '#0A2540',   
          light: '#F8F9FA',  
          border: '#E2E8F0', 
        },
        alert: {
          red: '#EF4444',    
          yellow: '#F59E0B', 
          green: '#10B981',  
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'], 
      }
    },
  },
  plugins: [],
}