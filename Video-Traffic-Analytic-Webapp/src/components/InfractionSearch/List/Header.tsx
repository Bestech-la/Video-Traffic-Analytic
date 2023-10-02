import React from 'react';
import { ColumnDef } from '@tanstack/react-table';
import moment from 'moment';
import { InfractionSearchShow } from '@components/InfractionSearch/Show';

export const Header = (): ColumnDef<any>[] => {
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
              className='h-[100px] w-[200px] m-auto object-fill'
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
              className='h-[200px] w-[200px] m-auto object-cover'
            />
          </div>
        );
      },
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
      header: 'ເບີ່ງລາຍລະອຽດ',
      cell: function render ({ getValue }) {
        const value = getValue() as number | undefined;
        return (
          <div className='hover:text-blue-500 text-lg text-center'>
            <InfractionSearchShow value={value}/>
          </div>
        );
      },
    },
  ];
};
