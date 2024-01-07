/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from 'react';
import { useNavigation } from '@refinedev/core';
import { useTable } from '@refinedev/react-table';
import { flexRender } from '@tanstack/react-table';
import { Pagination } from '@components/common/Pagination/Pagination';
import { Header } from './Header';
import { Filter } from './Filter';

export const InfractionTrackerList: React.FC = () => {
  const { edit, show } = useNavigation();
  const columns = React.useMemo(
    () => Header(),
    [edit, show],
  );

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
    },
    columns,
  });

  setOptions((prev) => ({
    ...prev,
    meta: {
      ...prev.meta,
    },
  }));
  // console.log("tableData", tableData)
  Filter.defaultProps={ refineCore };
  return (
    <>
      <div className='p-5 bg-gray-200 rounded-lg'>
        <div className='flex flex-col h-auto max-w-full px-4 py-10 mx-auto bg-white rounded-lg sm:px-6 lg:px-8 lg:py-14'>
          <div className='text-2xl text-center'>ລາຍງຍລົດທີ່ລ່ວງລະເມີດ</div>
          <div className='flex justify-end mb-5'>
            {/* <Filter refineCore={undefined} /> */}
          </div>
          <div className='flex flex-col'>
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
    </>
  );
};
