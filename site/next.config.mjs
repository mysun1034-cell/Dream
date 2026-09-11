/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      { source: "/resume/ko", destination: "/resume/ko.html" },
      { source: "/resume/en", destination: "/resume/en.html" },
    ];
  },
};

export default nextConfig;
