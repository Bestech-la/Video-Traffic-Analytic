import React from 'react';
import { ColumnDef } from '@tanstack/react-table';
import moment from 'moment';
import { IVehicleData } from '@components/InfractionTracker/interface';
import { InfractionSearchShow } from '@components/InfractionTracker/Show';

export const Header = (): ColumnDef<IVehicleData>[] => {
  return [
    {
      header: '#',
      accessorKey: '',
      cell: (props) => {
        return <div>{props.row.index + 1}</div>;
      },
    },
    {
      id: 'image_one',
      header: 'ຮູບພາບທີ 1',
      accessorKey: 'image_one',
      cell ({ row }) {
        const rowData = row.original;
        return (
          <div>
            <img src={rowData.image_two} alt="bill_2" className="h-[300pxpx] w-[300px] m-auto object-fill" />
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
              ເວລາ: <span>{moment(rowData.date_time).format('YYYY-MM-DD HH:mm:ss')}</span>
            </div>
            <div className="text-lg text-center">
              ສີລົດ: <span>{rowData.vehicle_color}</span>
            </div>
            <div className="text-lg text-center">
              ສີປ້າຍ: <span>{rowData.vehicle_registration_color}</span>
            </div>
            <div className="text-lg text-center">
             ແຂວງ: <span>{rowData.province}</span>
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
      header: 'ເບີ່ງຂໍມູນລົດ',
      cell ({ getValue }) {
        const value = getValue() as number | undefined;
        return (
          <div className="text-lg text-center">
            <InfractionSearchShow value={value} />
          </div>
        );
      },
    },
  ];
};
