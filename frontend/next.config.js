/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*'
      },
      {
        source: '/mcp/:path*',
        destination: 'http://localhost:8000/mcp/:path*'
      }
    ];
  }
};

module.exports = nextConfig;
