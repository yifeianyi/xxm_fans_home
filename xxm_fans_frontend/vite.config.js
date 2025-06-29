import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [vue()],
    server: {
        host: '0.0.0.0', // ✅ 允许手机访问前端
        port: 5173,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000', // ✅ 改成你电脑的局域网 IP（不是 localhost）
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, '/api')
            }
        }
    }
})
