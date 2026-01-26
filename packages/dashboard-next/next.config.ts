import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/proxy/:path*",
        destination: "http://dashboard-server-obyf.onrender.com/api/v1/:path*",
      },
    ];
  },
};

export default nextConfig;
