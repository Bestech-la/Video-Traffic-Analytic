/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from 'react';
import { useNavigation, useList } from '@refinedev/core';
import { useTable } from '@refinedev/react-table';
import { Filters } from './Filter';
import { flexRender } from '@tanstack/react-table';
import { Pagination } from '@components/common/Pagination/Pagination';
import { Header } from './Header';

import { CardDetail } from '@components/InfractionSearch/List/cardDetail';
export const InfractionSearchList: React.FC = ({}) => {
  const [platNumber, setPlatNumber] = React.useState('0');
  const { data: tracker_data } = useList<any>({
    resource: 'infraction_tracker',
    filters: [
      {
        field: 'vehicle_registration_number',
        operator: 'eq',
        value: platNumber,
      },
    ],
  });

  const { edit, show } = useNavigation();
  const columns = React.useMemo(() => Header(), [edit, show]);

  const {
    getHeaderGroups,
    getRowModel,
    setOptions,
    refineCore: {
      tableQueryResult: { data: tableData },
    },
    getState,
    setPageIndex,
    getCanPreviousPage,
    getPageCount,
    getCanNextPage,
    setPageSize,
    refineCore,
  } = useTable({
    refineCoreProps: {
      resource: 'infraction_tracker',
      filters: {
        initial: [
          {
            field: 'vehicle_registration_number',
            operator: 'eq',
            value: '00',
          },
        ],
      },
    },
    columns,
  });

  setOptions((prev) => ({
    ...prev,
    meta: {
      ...prev.meta,
    },
  }));
  Filters.defaultProps = { refineCore };
  return (
    <div className='flex flex-row justify-center w-3/4 p-2 mx-auto overflow-scroll md:flex-col gap-x-5 gap-y-5'>
      <div className='space-y-2 '>
        <Filters refineCore={undefined} setPlatNumber={setPlatNumber} />
        <CardDetail tracker_data={tracker_data} />
      </div>

      <div className='w-full p-5 bg-gray-200 rounded-lg '>
        <div className='flex flex-col h-auto max-w-full px-4 py-10 mx-auto bg-white rounded-lg sm:px-6 lg:px-8 lg:py-14'>
          <div className='text-2xl text-center'>ຄົ້ນຫາລົດທີ່ລ່ວງລະເມີດ</div>
          <div className='flex mb-5'></div>
          <div className='flex gap-2'>
            <div className='w-full'>
              <div className='-m-1.5 overflow-x-auto'>
                <div className='p-1.5 min-w-full inline-block align-middle'>
                  <div className='z-10 h-full overflow-hidden bg-white border border-gray-200 shadow-sm rounded-xl dark:bg-slate-900 dark:border-gray-700'>
                    <table className='min-w-full divide-y divide-gray-400 dark:divide-gray-700'>
                      <thead className='bg-gray-50 dark:bg-gray-700'>
                        {getHeaderGroups().map((headerGroup) => (
                          <tr key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                              <th
                                key={header.id}
                                scope='col'
                                className='px-6 py-3 text-xs font-medium text-center text-gray-500 uppercase'
                              >
                                {!header.isPlaceholder &&
                                  flexRender(
                                    header.column.columnDef.header,
                                    header.getContext(),
                                  )}
                              </th>
                            ))}
                          </tr>
                        ))}
                      </thead>
                      <tbody className='divide-y divide-gray-400 dark:divide-gray-700'>
                        {getRowModel().rows.map((row) => (
                          <tr key={row.id} className='text-center '>
                            {row.getVisibleCells().map((cell) => (
                              <td
                                key={cell.id}
                                className='px-6 py-4 text-sm text-gray-800 whitespace-nowrap dark:text-gray-200'
                              >
                                {flexRender(
                                  cell.column.columnDef.cell,
                                  cell.getContext(),
                                )}
                                s
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    <div className='grid gap-3 px-6 py-4 border-t border-gray-200 md:flex md:justify-between md:items-center dark:border-gray-700'>
                      <Pagination
                        getState={getState}
                        setPageSize={setPageSize}
                        setPageIndex={setPageIndex}
                        getCanPreviousPage={getCanPreviousPage}
                        getPageCount={getPageCount}
                        getCanNextPage={getCanNextPage}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
