import React from 'react';
import { type Story } from '@storybook/react';
import { LoginComponent } from '@components/login';
import { RefineWithoutLayout } from '../../.storybook/RefineWithoutLayout';

export default {
  title: 'Login',
  component: LoginComponent,
  decorators: [(Story: React.FC) => RefineWithoutLayout(Story)],
};

const Template: Story = (args) => <LoginComponent csrfToken={''} {...args} />;

export const Default = Template.bind({});
Default.args = {};
