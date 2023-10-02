import type { Preview } from "@storybook/react";
import "../src/styles/globals.css";

import { RefineWithoutLayout } from "./RefineWithoutLayout";
import('preline')
export const decorators = [RefineWithoutLayout];

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
  },
};

export default preview;
