/* eslint-disable no-unused-vars */
import React from 'react';
import { MdOutlineKeyboardDoubleArrowLeft, MdOutlineKeyboardDoubleArrowRight } from 'react-icons/md';

interface PaginationProps {
  getState: () => any
  setPageSize: (size: number) => void
  setPageIndex: (index: number) => void
  getCanPreviousPage: () => boolean
  getPageCount: () => number
  getCanNextPage: () => boolean
}

export const Pagination: React.FC<PaginationProps> = ({ getState, setPageSize, setPageIndex, getCanPreviousPage, getPageCount, getCanNextPage }) => {
  return (
    <div className="py-1 px-4">
      <nav className="flex items-center space-x-2">
        <select
          className="py-2 px-4 bg-white text-gray-600 font-medium rounded hover:bg-gray-100 active:bg-gray-200 disabled:opacity-50 inline-flex items-center"
          value={getState().pagination.pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
          }}
        >
          {[20, 30, 40, 50, 60].map((pageSize) => (
            <option key={pageSize} value={pageSize}>
              ສະແດງ {pageSize}
            </option>
          ))}
        </select>
        <button
          onClick={() => {
            setPageIndex(0);
          }}
          disabled={!getCanPreviousPage()}
          className="p-2 rounded hover:bg-gray-100"
        >
          <MdOutlineKeyboardDoubleArrowLeft className="h-6 w-6" />
        </button>
        {Array.from({ length: getPageCount() }, (_, index) => (
          <button
            key={index}
            onClick={() => {
              setPageIndex(index);
            }}
            className={`w-10 h-10 text-gray-400 hover:text-blue-600 p-4 inline-flex items-center text-sm font-medium rounded-lg
                    ${getState().pagination.pageIndex === index ? 'bg-blue-500 text-white' : ''}`}
          >
            {index + 1}
          </button>
        ))}
        <button
          onClick={() => {
            setPageIndex(getPageCount() - 1);
          }}
          disabled={!getCanNextPage()}
          className="p-2 ml-1 rounded hover:bg-gray-100"
        >
          <MdOutlineKeyboardDoubleArrowRight className="h-6 w-6" />
        </button>
      </nav>
    </div>
  );
};
