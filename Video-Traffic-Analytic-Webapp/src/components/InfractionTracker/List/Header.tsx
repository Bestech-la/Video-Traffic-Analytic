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
        return (
          <>
            <div>{props.row.index + 1}</div>
          </>
        );
      },
    },
    {
      id: 'image_one',
      header: 'ຮູບພາບທີ 1',
      accessorKey: 'image_one',
      cell: function render ({ getValue }) {
        const image = getValue() as string;
        return (
          <div>
            <img
              src={image}
              alt='bill'
              className='h-[120px] w-[300px] m-auto object-fill'
            />
          </div>
        );
      },
    },
    {
      id: 'image_two',
      header: 'ຮູບພາບທີ 2',
      accessorKey: 'image_two',
      cell: function render ({ getValue }) {
        const image = getValue() as string;
        return (
          <div>
            <img
              src={image}
              alt='bill'
              className='h-[250px] w-[250px] m-auto object-cover'
            />
          </div>
        );
      },
    },
    {
      id: 'vehicle_registration_number',
      accessorKey: 'vehicle_registration_number',
      header: 'ປ້າຍລົດ',
    },
    {
      id: 'created_on',
      accessorKey: 'created_on',
      header: 'ເວລາລ່ວງລະເມີດ',
      cell: function render ({ getValue }) {
        const date = getValue() as string;
        return (
          <div className='text-lg text-center'>
            {moment(date).format('llll')}
          </div>
        );
      },
    },
    {
      id: 'actions',
      accessorKey: 'id',
      header: 'ແກ້ໄຂ',
      cell: function render ({ getValue }) {
        const value = getValue() as number | undefined;
        return (
          <div className='text-lg text-center'>
            <InfractionSearchShow value={value} />
          </div>
        );
      },
    },
  ];
};
