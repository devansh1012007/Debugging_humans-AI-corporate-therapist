import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()], // Tells Vite "We are using React, please handle .jsx files correctly"
})