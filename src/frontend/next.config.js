// src/frontend/next.config.js

/** @type {import('next').NextConfig} */
const nextConfig = {
  // ===== COMPILER OPTIMIZATIONS =====

  // ===== IMAGE OPTIMIZATION =====
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 86400,
  },

  // ===== BUNDLE ANALYSIS =====
  webpack: (config, { isServer }) => {
    config.performance = {
      hints: 'warning',
      maxEntrypointSize: 1000000,
      maxAssetSize: 500000,
    };

    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        radix: {
          test: /[\\/]node_modules[\\/]@radix-ui[\\/]/,
          name: 'radix-ui',
          chunks: 'all',
          priority: 20,
          reuseExistingChunk: true,
        },
        tanstack: {
          test: /[\\/]node_modules[\\/]@tanstack[\\/]/,
          name: 'tanstack',
          chunks: 'all',
          priority: 25,
          reuseExistingChunk: true,
        },
      },
    };

    return config;
  },

  // ===== PRODUCTION OPTIMIZATIONS =====
  productionBrowserSourceMaps: false,
  compress: true,
  swcMinify: true,
  poweredByHeader: false,
  reactStrictMode: true,

  // ===== CODE SPLITTING =====
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-*', 'sonner', 'axios', 'next-intl', 'class-variance-authority', 'clsx', 'tailwind-merge'],
  },

  // ===== SECURITY & CACHING HEADERS =====
  headers: async () => {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
          },
        ],
      },
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, s-maxage=60, stale-while-revalidate=300',
          },
        ],
      },
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/:path(.+\\.(?:ico|png|jpg|jpeg|gif|webp|avif|svg|woff|woff2|ttf|eot))',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/:path(.+\\.(?:js|css))',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
