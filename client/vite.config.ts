import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // 모든 IP에서 접근 가능
    port: 18080,      // 외부 노출 포트
    strictPort: true, // 포트가 사용 중이면 에러 발생
  }
})
