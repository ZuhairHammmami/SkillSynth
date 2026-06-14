// src/frontend/next.config.js

/** @type {import('next').NextConfig} */
const nextConfig = {
  // ===== COMPILER OPTIMIZATIONS =====
  // reactCompiler removed - not supported in this Next.js version
  
  // ===== IMAGE OPTIMIZATION =====
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    // Enable static imports for images
    formats: ['image/webp', 'image/avif'],
    // Responsive images optimization
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },

  // ===== BUNDLE ANALYSIS =====
  webpack: (config, { isServer }) => {
    // Performance hint for large chunks
    config.performance = {
      hints: 'warning',
      maxEntrypointSize: 512000,
      maxAssetSize: 512000,
    };

    return config;
  },

  // ===== PRODUCTION OPTIMIZATIONS =====
  productionBrowserSourceMaps: false,
  compress: true,
  
  // ===== CODE SPLITTING =====
  experimental: {
    optimizePackageImports: ['lucide-react', '@radix-ui/react-*'],
  },

  // ===== HEADERS FOR CACHING =====
  headers: async () => {
    return [
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
    ];
  },
};

module.exports = nextConfig;
