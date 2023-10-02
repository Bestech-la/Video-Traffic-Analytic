module.exports = {
  stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|ts|tsx)"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "@tomfreudenberg/next-auth-mock/storybook",
  ],
  core: {
    builder: "webpack5",
  },
  framework: {
    name: "@storybook/nextjs",
    options: {},
  },
  docs: {
    autodocs: "tag",
  },
  webpackFinal: async (config) => {
    config.experiments = { topLevelAwait: true };
    return config;
  },
  staticDirs: ["../public"],
};
