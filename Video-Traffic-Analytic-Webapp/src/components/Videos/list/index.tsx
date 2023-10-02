import React, { useState, useRef } from 'react';
import { useList } from '@refinedev/core';
import { AiFillPlayCircle } from 'react-icons/ai';
export const VideoList: React.FC = () => {
  const { data: videoData } = useList({
    resource: 'video',
  });
  const [videoUrl, setVideoUrl] = useState<string | undefined>();
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const playVideo = (videoLink: string) => {
    setVideoUrl(videoLink);
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play();
    }
  };

  return (
    <div >
      <div className=" justify-center flex bg-white  rounded-lg py-2">
        <div className="h-[600px] w-[600px] bg-gray-300 rounded-lg  ">
          <video
            ref={videoRef}
            className=" justify-center my-auto h-[600px] w-[600px]"
            controls
          >
            <source src={videoUrl} />
          </video>
        </div>
        <div className="h-[600px] w-[300px] overflow-scroll px-3 py-5 flex-col ">
          {videoData?.data?.map((item, index) => (
            <div
              key={index}
              className="my-2 relative bg-gray-300 p-2 rounded-lg "
              onClick={() => playVideo(item.video)}
            >
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <AiFillPlayCircle
                  size={48}
                  onClick={() => playVideo(videoData?.data?.[0]?.video)}
                />
              </div>
              <video>
                <source src={item?.video} />
              </video>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
