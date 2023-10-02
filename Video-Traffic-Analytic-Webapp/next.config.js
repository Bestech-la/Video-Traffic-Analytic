module.exports = {
  experiments: {
    topLevelAwait: true,
    newNextLinkBehavior: true,
  },
  webpack: (config) => {
    config.experiments = { ...config.experiments, topLevelAwait: true };
    return config;
  },
  images: {
    domains: ["127.0.0.1"],
  },
};
