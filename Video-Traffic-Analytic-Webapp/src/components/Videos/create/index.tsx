import React, { useState, useEffect, useRef } from 'react';
import { Modal } from '@components/common/Modal';
import { useModalForm } from '@refinedev/react-hook-form';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export const VideosCreate: React.FC = ({}) => {
  const {
    refineCore: { onFinish, formLoading },
    register,
    handleSubmit,
    setValue,
    modal: { visible, close, show },
    watch,
  } = useModalForm({
    refineCoreProps: {
      action: 'create',
      resource: 'video',
      meta: {
        headers: {
          'content-type': 'multipart/form-data',
        },
      },
    },
    // resolver: yupResolver(schema),
  });

  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [videoHeight, setVideoHeight] = useState<number>(100);
  const VideoW = videoHeight ?? 100;
  const [yOne, setYOne] = useState<number>();
  const [yTwo, setYTwo] = useState<number>();
  
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const onSubmit = async (data: any) => {
    try {
      const response = await onFinish(data);
      if (response) {
        toast.success('created video');
        close();
      }
    } catch (error) {}
  };

  const selectedVideoFile = watch('video');

  useEffect(() => {
    if (selectedVideoFile) {
      setSelectedVideo(selectedVideoFile[0]);
      videoRef.current?.load();
      videoRef.current?.addEventListener('loadedmetadata', () => {
        setVideoHeight(videoRef.current?.videoHeight ?? 100);
      });
    }
  }, [selectedVideoFile]);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name;
    const value = parseInt(event.target.value, 10);
    if (name === 'yOne') {
      const greenLine = videoHeight - value;
      setYOne(greenLine);
    } else if (name === 'yTwo') {
      const redLine = videoHeight - value;
      setYTwo(redLine);
    }
  };

  useEffect(() => {
    setValue('yOne',yOne);
  }, [yOne]);
  
  useEffect(() => {
    setValue('yTwo',yTwo);
  }, [yTwo]);

  return (
    <>
      <ToastContainer />
      <button
        role='open_modal'
        type="button"
        className="py-3 px-4 w-44 m-2 inline-flex justify-center items-center gap-2 rounded-md border border-transparent font-semibold bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all text-sm dark:focus:ring-offset-gray-800"
        onClick={() => show()}
      >
        ເພີ່ມວິດີໂອ
      </button>

      <Modal isOpen={visible} onClose={close}>
        <form
          className=""
          onSubmit={handleSubmit(onSubmit)}
          encType="multipart/form-data"
        >
          <div className=" w-[720px] bg-white md:mx-0 shadow-xl rounded-2xl sm:p-10 border border-gray-400 p-5 text-left ">
            <div className="flex relative justify-center">
              <div className="pt-[195px] flex w-[720px] z-10 absolute top-0  right-[80px]">
                <input
                  type="range"
                  className="rotate-90 h-2 w-[350px] cursor-ew-resize appearance-none rounded-full  disabled:cursor-not-allowed bg-green-500"
                  min={0}
                  max={VideoW}
                  name="yOne"
                  onChange={handleChange}
                />
              </div>
              <div className="relative">
                <video
                  controls
                  ref={videoRef}
                  className="justify-center my-auto h-[400px] w-[750px]"
                >
                  {selectedVideo && (
                    <source src={URL.createObjectURL(selectedVideo)} />
                  )}
                </video>
              </div>
              <div className="pt-[195px] flex w-[720px] pr-20 z-10 absolute top-0  left-[435px]">
                <input
                  type="range"
                  className="rotate-90 h-2 w-[350px] cursor-ew-resize appearance-none rounded-full  disabled:cursor-not-allowed bg-red-500"
                  min={0}
                  max={VideoW}
                  name="yTwo"
                  onChange={handleChange}
                />
              </div>
            </div>
            <div className="w-full px-3 mb-6 md:mb-0">
              <h1 className="ml-1">ວີດີໂອ</h1>
              <input
                className="px-4 w-full py-2 h-10 border focus:ring-gray-500 focus:border-base sm:text-sm border-gray-300 rounded-md focus:outline-none"
                type="file"
                {...register('video')}
                aria-label="video"
              />
            </div>
            <div className="w-full px-3 mt-3 md:mb-0 flex gap-x-2">
              <button
                type="button"
                onClick={close}
                className="w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border border-transparent font-semibold bg-red-500 text-white hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all text-sm dark:focus:ring-offset-gray-800"
              >
                ຍົກເລີກ
              </button>
              <button
                role="ບັນທືກ"
                type="submit"
                className="w-full py-3 px-4 inline-flex justify-center items-items-center gap-2 rounded-md border border-transparent font-semibold bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all text-sm dark:focus:ring-offset-gray-800"
              >
                {formLoading ? 'Loading' : '  ບັນທືກ'}
              </button>
            </div>
          </div>
        </form>
      </Modal>
    </>
  );
};
