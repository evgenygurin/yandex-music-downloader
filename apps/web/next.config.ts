import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },

  // Optimize for production
  poweredByHeader: false,
  compress: true,
  reactStrictMode: true,
  
  // Performance optimizations
  experimental: {
    optimizePackageImports: ["lucide-react", "@radix-ui/react-dialog", "@radix-ui/react-select"],
  },

  // Image optimization
  images: {
    formats: ["image/avif", "image/webp"],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
    contentDispositionType: "attachment",
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // Turbopack configuration (replaces webpack)
  turbopack: {
    // Empty config to enable Turbopack with default settings
  },
};

export default nextConfig;
