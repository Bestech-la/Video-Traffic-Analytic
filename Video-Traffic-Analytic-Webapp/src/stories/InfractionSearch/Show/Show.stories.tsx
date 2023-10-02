/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
import { InfractionSearchList } from '@components/InfractionSearch';
import { RefineWithoutLayout } from '../../../../.storybook/RefineWithoutLayout';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof InfractionSearchList> = {
  title: 'InfractionSearch/InfractionSearchList',
  component: InfractionSearchList,
  render: (args, { loaded: {} }) => (
    <InfractionSearchList  />
  ),
  parameters: {
    nextjs: {
      router: {
        basePath: '/',
      },
    },
  },
  decorators: [(Story: React.FC) => RefineWithoutLayout(Story)],
};

export default meta;
type Story = StoryObj<typeof InfractionSearchList>;

export const show: Story = {
  loaders: [],
};


