import React from 'react';
export interface IVehicleData {
  id: number
  image_one: string
  image_two: string
  vehicle_registration_number: string
  brand: string
  vehicle_color: string
  vehicle_registration_color: string
  province: string
  created_on: string
}

export const CardDetail: React.FC<any> = ({ tracker_data }) => {
  return (
    <div className=" rounded-lg h-96 w-96 flex flex-col  border">
      <div className="text-xl  text-center pt-5"> ລາຍລະອຽດ</div>
      <div className="bg-white rounded-lg  text-xl pl-5">
        <div className=" p-2 ">
          ປ້າຍລົດ:
          {tracker_data ? tracker_data?.data?.[0]?.vehicle_registration_number : ''}
        </div>
        <div className=" p-2">ຍີ້ຫໍ້ລົດ: {tracker_data ? tracker_data?.data?.[0]?.brand : ''}</div>
        <div className=" p-2">ສີລົດ: {tracker_data ? tracker_data?.data?.[0]?.vehicle_color : ''}</div>
        <div className=" p-2">ປະເພດສີປ້າຍ: {tracker_data ? tracker_data?.data?.[0]?.vehicle_registration_color : ''}</div>
        <div className=" p-2">ແຂວງ: {tracker_data ? tracker_data?.data?.[0]?.province : ''}</div>
        <div className=" p-2">ຈໍານວນລ່ວງລະເມີດ: {tracker_data ? tracker_data?.total : ''} ຄັ້ງ</div>
      </div>
    </div>
  );
};
