/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
import { VideosCreate } from '@components/Videos';
import { RefineWithoutLayout } from '../../../../.storybook/RefineWithoutLayout';
import { FC } from 'react';

export const List: typeof VideosCreate = (args) => <VideosCreate />;

export default {
  title: 'Videos/create',
  component: VideosCreate,
  parameters: {
    nextjs: {
      router: {
        basePath: '',
      },
    },
  },
  argTypes: {
    title: {
      type: 'string',
    },
  },
  decorators: [(Story: FC) => RefineWithoutLayout(Story)],
};
