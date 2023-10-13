module.exports = {
  experiments: {
    topLevelAwait: true,
    newNextLinkBehavior: true,
  },
  webpack: (config) => {
    config.experiments = { ...config.experiments, topLevelAwait: true }
    return config
  },
  images: {
    domains: ['127.0.0.1'],
  },
  output: 'standalone',
  serverRuntimeConfig: {
    SECRET_KEY: process.env.SECRET_KEY,
    API_ENDPOINT: process.env.API_ENDPOINT,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXTAUTH_URL_INTERNAL: process.env.NEXTAUTH_URL_INTERNAL,
  },
  publicRuntimeConfig: {
    API_ENDPOINT: process.env.API_ENDPOINT,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    NEXTAUTH_URL_INTERNAL: process.env.NEXTAUTH_URL_INTERNAL,
  },
}
