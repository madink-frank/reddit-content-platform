/// <reference types="vitest" />
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isProduction = mode === 'production'
  
  return {
    plugins: [
      react({
        // Optimize JSX in production
        jsxRuntime: 'automatic',
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    define: {
      // Replace environment variables at build time
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },
    build: {
      // Target modern browsers for better optimization
      target: 'es2020',
      // Optimize chunk size
      chunkSizeWarningLimit: 1000,
      // Enable source maps for production debugging (can be disabled for smaller builds)
      sourcemap: isProduction ? 'hidden' : true,
      // Minification options
      minify: isProduction ? 'esbuild' : false,
      // CSS code splitting
      cssCodeSplit: true,
      // Rollup options for advanced optimization
      rollupOptions: {
        output: {
          // Manual chunk splitting for optimal caching
          manualChunks: (id) => {
            // Vendor chunks
            if (id.includes('node_modules')) {
              if (id.includes('react') || id.includes('react-dom')) {
                return 'react-vendor'
              }
              if (id.includes('react-router')) {
                return 'router'
              }
              if (id.includes('@headlessui') || id.includes('@heroicons')) {
                return 'ui-vendor'
              }
              if (id.includes('chart.js') || id.includes('react-chartjs-2')) {
                return 'charts'
              }
              if (id.includes('axios') || id.includes('@tanstack/react-query')) {
                return 'api-vendor'
              }
              if (id.includes('zustand') || id.includes('immer')) {
                return 'state-vendor'
              }
              if (id.includes('date-fns') || id.includes('clsx') || id.includes('lucide-react')) {
                return 'utils-vendor'
              }
              // Other vendor libraries
              return 'vendor'
            }
            
            // App chunks
            if (id.includes('/src/pages/')) {
              return 'pages'
            }
            if (id.includes('/src/components/')) {
              return 'components'
            }
            if (id.includes('/src/services/') || id.includes('/src/hooks/')) {
              return 'services'
            }
          },
          // Optimize asset file names
          assetFileNames: (assetInfo) => {
            if (!assetInfo.name) return `assets/[name]-[hash][extname]`
            
            if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name)) {
              return `assets/images/[name]-[hash][extname]`
            }
            if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
              return `assets/fonts/[name]-[hash][extname]`
            }
            return `assets/[name]-[hash][extname]`
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
        },
      },
      // Optimize dependencies
      commonjsOptions: {
        include: [/node_modules/],
      },
    },
    // Performance optimizations
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react-router-dom',
        '@headlessui/react',
        '@heroicons/react/24/outline',
        '@heroicons/react/24/solid',
        'chart.js',
        'react-chartjs-2',
        'chartjs-adapter-date-fns',
        'date-fns',
        'axios',
        'zustand',
        '@tanstack/react-query',
        'clsx',
        'lucide-react',
        'socket.io-client',
      ],
      // Force optimization of these packages
      force: isProduction,
    },
    // Server configuration for development
    server: {
      port: 5173,
      host: true,
      cors: true,
      // Proxy API requests in development
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    // Preview server configuration
    preview: {
      port: 4173,
      host: true,
      cors: true,
    },
    // Test configuration
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        exclude: [
          'node_modules/',
          'src/test/',
          '**/*.d.ts',
          '**/*.config.*',
          'dist/',
          'coverage/',
          '**/*.test.*',
          '**/*.spec.*',
        ],
        thresholds: {
          global: {
            branches: 70,
            functions: 70,
            lines: 70,
            statements: 70,
          },
        },
      },
    },
  }
})