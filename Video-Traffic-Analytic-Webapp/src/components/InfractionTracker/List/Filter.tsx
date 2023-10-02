import React from 'react';
import Datetime from 'react-datetime';
import moment from 'moment';
import 'react-datetime/css/react-datetime.css';
import { Controller } from 'react-hook-form';
import { useForm } from 'react-hook-form';

interface IFilter {
  refineCore: any;
}


export const Filter: React.FC<IFilter> = ({ refineCore }) => {
  const { handleSubmit, control } = useForm();

  const applyFilter = (filterDate: any) => {
    refineCore.setFilters([
      {
        field: 'created_on',
        operator: 'eq',
        value: filterDate,
      },
    ]);
  };

  return (
    <form className="w-72 z-10" onSubmit={handleSubmit((formData) => {
      const filterDate = formData.filterDate || '';
      applyFilter(filterDate);
    })}>
      <div className="w-full relative flex rounded-md shadow-sm border">
        <Controller
          control={control}
          name="filterDate" 
          render={({ field }) => (
            <Datetime
              onChange={(date) => {
                const formattedDate = moment(date).format('YYYY-MM-DD');
                field.onChange(formattedDate);
              }}
              renderInput={(props) => (
                <input
                  {...props}
                  className="py-3 px-4 pl-11 block w-full border-gray-200 shadow-sm rounded-l-md text-sm focus:z-10 focus:border-blue-500 focus:ring-blue-500 dark:bg-slate-900 dark:border-gray-700 dark:text-gray-400"
                />
              )}
              initialValue={moment(field.value)}
              dateFormat="DD-MM-YYYY"
              timeFormat=""
            />
          )}
        />
        <button
          type="submit"
          className="py-3 px-5 inline-flex flex-shrink-0 justify-center items-center rounded-r-md border border-transparent font-semibold bg-blue-500 text-white hover:bg-blue-600 focus:z-10 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all text-sm"
        >
          ຄົ້ນຫາ
        </button>
      </div>
    </form>
  );
};
