/** @type {import('next').NextConfig} */
const nextConfig = {
  // Use standard Next.js server mode for dynamic routes and API-based data.
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
}

export default nextConfig