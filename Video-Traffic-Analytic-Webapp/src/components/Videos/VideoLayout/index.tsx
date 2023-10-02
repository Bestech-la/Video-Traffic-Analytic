import React from 'react';
import { VideoList } from '@components/Videos/list';
import { VideosCreate } from '@components/Videos/create';

export const VideoLayout: React.FC = () => {
  return (
    <div className='w-3/4 mx-auto gap-x-2  bg-gray-300 p-5 rounded-lg'>
      <VideosCreate />
      <VideoList />
    </div>
  );
};
