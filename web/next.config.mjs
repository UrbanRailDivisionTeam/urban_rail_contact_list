/** @type {import('next').NextConfig} */
const isDev = process.env.NODE_ENV === "development"

/** @type {import('next').NextConfig} */
const nextConfig = {
    output: isDev ? undefined : "export",
    basePath: isDev ? undefined : "/static",
    assetPrefix: isDev ? undefined : "/static",
    trailingSlash: true,
    async rewrites() {
        if (!isDev) return []
        return [
            {
                source: "/api/:path*",
                destination: "http://localhost:12379/api/:path*",
            },
        ]
    },
}

export default nextConfig
