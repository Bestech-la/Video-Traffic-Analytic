import React from 'react';

type ModalPropsType = {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
};

export const Modal: React.FC<ModalPropsType> = ({
  isOpen,
  children,
}) => {
  if (!isOpen) return null;
  return (
    <div role="dialog">
      {isOpen ? (
        <>
          <div className="transition  duration-300 delay-300 ease-in-out justify-center items-center flex overflow-x-hidden overflow-y-auto fixed inset-0 z-50 outline-none focus:outline-none">
            <div className="relative w-auto my-6 mx-auto max-w-3xl">
              <div className="modal-content">{children}</div>
            </div>
          </div>
          <div className="opacity-25 fixed inset-0 z-40 bg-black" />
        </>
      ) : null}
    </div>
  );
};
