/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
import { InfractionSearchShow } from '@components/InfractionSearch';
import { RefineWithoutLayout } from '../../../../.storybook/RefineWithoutLayout';
import type { Meta, StoryObj } from '@storybook/react';

const meta: Meta<typeof InfractionSearchShow> = {
  title: 'InfractionSearch/InfractionSearchShow',
  component: InfractionSearchShow,
  render: (args, { loaded: {} }) => (
    <InfractionSearchShow value={undefined} />
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
type Story = StoryObj<typeof InfractionSearchShow>;

export const show: Story = {
  loaders: [],
};
