import React from 'react';
import { Controller } from 'react-hook-form';
import { useForm } from '@refinedev/react-hook-form';
import 'react-datetime/css/react-datetime.css';
import Datetime from 'react-datetime';
import Moment from 'moment';

export const SelectDateTime: React.FC = () => {
  const {
    refineCore: { onFinish },
    handleSubmit,
    control,
  } = useForm({
    refineCoreProps: {},
  });
  return (
    <form className=' mx-5 my-2 ' onSubmit={handleSubmit(onFinish)}>
      <div className='w-full '>
        <div>ຄົນຫາຕາມວັນທີ</div>
        <Controller
          control={control}
          name='start_date'
          render={({ field }) => (
            <Datetime
              onChange={(date) => {
                const formattedDate = Moment(date).format('YYYY-MM-DDTHH:mm');
                field.onChange(formattedDate);
              }}
              renderInput={(props) => (
                <input
                  {...props}
                  className='px-4 w-full py-2 h-10 border focus:ring-gray-500 focus:border-base sm:text-sm border-gray-300 rounded-md focus:outline-none text-gray-600 p-5'
                />
              )}
              initialValue={Moment(field.value)}
              dateFormat='DD-MM-YYYY'
            />
          )}
        />
      </div>
    </form>
  );
};
