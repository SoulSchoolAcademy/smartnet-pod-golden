/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const base = process.env.LEDGER_BASE_URL || 'http://localhost:4000';
    return [
      { source: '/truth/:path*', destination: ${base}/api/truth/:path* },
      { source: '/verify/:path*', destination: ${base}/verify/:path* }
    ];
  }
};
export default nextConfig;