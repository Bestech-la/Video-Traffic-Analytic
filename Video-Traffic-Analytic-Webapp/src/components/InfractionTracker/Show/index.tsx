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
          className="py-3 px-4 w-44 m-2 inline-flex justify-center items-center gap-2 rounded-md border border-transparent font-semibold bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all text-sm dark:focus:ring-offset-gray-800"
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

          <div className="fixed inset-0 ">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
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
                  className=" transform  w-3/4 rounded-2xl bg-white
                text-left align-middle shadow-xl transition-all "
                >
                  <div className="flex flex-wrap  justify-center content-center  mb-6 mx-auto z-50">
                    <div className="bg-gray-200 rounded-lg p-5">
                      {value ? (
                        <div className="flex flex-col bg-white  rounded-lg p-2">
                          <div className="text-4xl  text-center my-5">ລາຍລະອຽດ</div>

                          <div className="flex gap-5">
                            <div className="flex flex-col">
                              <img src={showData?.image_two} alt="" className="h-[400px] w-full object-cover rounded-lg col-span-2" />
                              <img src={showData?.image_one} alt="" className="h-[200px] w-full object-fill rounded-lg col-span-2" />
                            </div>
                            <div className="bg-gray-200 rounded-lg   text-md space-y-2 pl-5 w-94 pt-5">
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

                    <div className="w-full  px-3 mt-3 md:mb-0 flex gap-x-2">
                      <button
                        type="button"
                        className="w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border border-transparent font-semibold bg-red-500 text-white hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all text-sm dark:focus:ring-offset-gray-800"
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
