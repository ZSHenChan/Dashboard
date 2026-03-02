import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const serverUrl = process.env.DASHBOARD_SERVER || "http://0.0.0.0:8000";

    return [
      {
        source: "/api/proxy/:path*",
        destination: `${serverUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
