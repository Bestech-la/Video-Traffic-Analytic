/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
import { InfractionTrackerList } from '@components/InfractionTracker';
import { RefineWithoutLayout } from '../../../../.storybook/RefineWithoutLayout';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof InfractionTrackerList> = {
  title: 'InfractionTracker/InfractionTrackerList',
  component: InfractionTrackerList,
  render: (args, { loaded: {} }) => (
    <InfractionTrackerList  />
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
type Story = StoryObj<typeof InfractionTrackerList>;

export const show: Story = {
  loaders: [],
};
