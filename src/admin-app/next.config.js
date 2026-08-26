/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: '**' },
    ],
  },
  productionBrowserSourceMaps: false,
  compress: true,
  swcMinify: true,
  poweredByHeader: false,
  reactStrictMode: true,
};

module.exports = nextConfig;
