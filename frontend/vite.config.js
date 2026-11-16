import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev-only proxy: the browser calls /api/courses, Vite forwards it to Flask as /courses.

export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            "/api": {
                target: "http://localhost:5000",
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, ""),
            },
        },
    },
});