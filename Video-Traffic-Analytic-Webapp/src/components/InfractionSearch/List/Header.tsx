import React from 'react';
import { ColumnDef } from '@tanstack/react-table';
import moment from 'moment';
import { InfractionSearchShow } from '@components/InfractionSearch/Show';

export const Header = (): ColumnDef<any>[] => {
  return [
    {
      id: 'image_one',
      header: 'ຮູບພາບທີ 1',
      accessorKey: 'image_one',
      cell ({ row }) {
        const rowData = row.original;
        return (
          <div className='w-40 '>
            <img src={rowData.image_two} alt="bill_2" className="h-[300pxpx] w-full m-auto object-fill" />
            <img src={rowData.image_one} alt="bill_1" className="h-[120px] w-[300px] m-auto object-fill" />
          </div>
        );
      },
    },
    {
      id: 'car_detail',
      header: 'ຂໍມູນລົດ',
      accessorKey: 'image_one',
      cell ({ row }) {
        const rowData = row.original;
        return (
          <div className="flex flex-col items-start p-5 text-black bg-gray-200 rounded-lg">
            <div className="text-lg text-center">
              ປ້າຍລົດ: <span>{rowData.vehicle_registration_number}</span>
            </div>
            <div className="text-lg text-center">
              ເວລາ: <span>{moment(rowData.created_on).format('llll')}</span>
            </div>
            <div className="text-lg text-center">
              ສີລົດ: <span>{rowData.vehicle_color}</span>
            </div>
            <div className="text-lg text-center">
              ສີປ້າຍ: <span>{rowData.vehicle_registration_color}</span>
            </div>
            <div className="text-lg text-center">
             ແຂວງ: <span>{}</span>
            </div>
            <div className="text-lg text-center">
            ຍີ້ຫໍ້ລົດ: <span>{}</span>
            </div>
          </div>
        );
      },
    },
    {
      id: 'actions',
      accessorKey: 'id',
      header: 'ເບີ່ງລາຍລະອຽດ',
      cell: function render({ getValue }) {
        const value = getValue() as number | undefined;
        return (
          <div className="text-lg text-center hover:text-blue-500">
            <InfractionSearchShow value={value} />
          </div>
        );
      },
    },
  ];
};
