import { IVehicleData } from '@components/InfractionTracker/interface';
import { Dialog, Transition } from '@headlessui/react';
import React, { Fragment, useState, useRef } from 'react';
import { useOne } from '@refinedev/core';
import moment from 'moment';

interface IInfractionTrackerShow {
  value: number | undefined;
}

export const InfractionSearchShow: React.FC<IInfractionTrackerShow> = ({ value }) => {
  const { data: infraction_tracker_data } = useOne<IVehicleData>({
    resource: 'infraction_tracker',
    id: value,
  });
  const showData = infraction_tracker_data?.data;

  const { data: videoData } = useOne({
    resource: 'video',
    id: showData?.video,
  });

  const videoRef = useRef<HTMLVideoElement | null>(null);

  const [isOpen, setIsOpen] = useState(false);
  function closeModal() {
    setIsOpen(false);
  }
  function openModal() {
    setIsOpen(true);
  }
  return (
    <>
      <div className="">
        <button
          type="button"
          onClick={openModal}
          className="inline-flex items-center justify-center gap-2 px-4 py-3 m-2 text-sm font-semibold text-white transition-all bg-blue-500 border border-transparent rounded-md w-44 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
        >
          ເບີ່ງລາຍລະອຽດ
        </button>
      </div>
      <Transition appear show={isOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={closeModal}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 h-screen overflow-y-auto ">
            <div className="flex items-center justify-center min-h-full p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel
                  className="w-3/4 text-left align-middle transition-all transform bg-white shadow-xl rounded-2xl"
                >
                  <div className="z-50 flex flex-wrap content-center justify-center mx-auto mb-6">
                    <div className="p-5 bg-gray-200 rounded-lg">
                      {value ? (
                        <div className="flex flex-col p-2 bg-white rounded-lg">
                          <div className="my-5 text-4xl text-center">ລາຍລະອຽດ</div>

                          <div className="flex flex-row gap-5 sm:flex-col">
                            <div className="flex flex-col">
                              <img src={showData?.image_two} alt="" className="h-[400px] w-full object-cover rounded-lg col-span-2" />
                              <img src={showData?.image_one} alt="" className="h-[200px] w-full object-fill rounded-lg col-span-2" />
                            </div>
                            <div className="pt-5 pl-5 space-y-2 bg-gray-200 rounded-lg text-md w-94">
                              <div className="p-1">ປ້າຍລົດ: {showData?.vehicle_registration_number}</div>
                              <div className="p-1"> ຍີ້ຫໍ້ລົດ: {showData?.brand}</div>
                              <div className="p-1">ສີລົດ: {showData?.vehicle_color}</div>
                              <div className="p-1">ປະເພດສີປ້າຍ: {showData?.vehicle_registration_color}</div>
                              <div className="p-1">ແຂວງ :{showData?.province}</div>
                              <div className="p-1">
                                ເວລາລ່ວງລະເມີດ:
                                {moment(showData?.created_on).format('llll')}
                              </div>
                            </div>
                            <video ref={videoRef} className=" justify-center my-auto h-[600px] w-[600px]" controls>
                              <source src={videoData?.data?.video} />
                            </video>
                          </div>
                        </div>
                      ) : (
                        ''
                      )}
                    </div>

                    <div className="flex w-full px-3 mt-3 md:mb-0 gap-x-2">
                      <button
                        type="button"
                        className="inline-flex items-center justify-center w-full gap-2 px-4 py-3 text-sm font-semibold text-white transition-all bg-red-500 border border-transparent rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
                        onClick={closeModal}
                      >
                        ຍົກເລີກ
                      </button>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </>
  );
};
