import React, { useState, type ReactNode } from 'react';

interface INavbar {
  children: ReactNode;
}
export const Navbar: React.FC<INavbar> = ({ children }) => {
  const [active, setActive] = useState('home');

  const handleLinkClick = (section: string) => {
    setActive(section);
  };

  return (
    <>
      <div >
        <header className="sticky top-0 inset-x-0 flex flex-wrap sm:justify-start sm:flex-nowrap z-[48] w-full bg-white border-b text-sm py-2.5 sm:py-4  dark:bg-gray-800 dark:border-gray-700">
          <nav className="bg-white dark:bg-gray-900 fixed w-full z-20 top-0 left-0 border-b border-gray-200 dark:border-gray-600">
            <div className="flex flex-wrap items-center justify-center mx-auto p-4">
              <ul className="flex flex-col p-4 md:p-0 mt-4 font-medium border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
                <li>
                  <a
                    href="#home"
                    className={`block py-2 pl-3 pr-4 text-gray-900 dark:text-white rounded hover:bg-gray-100  ${
                      active === 'home' ? 'font-bold bg-gray-200 p-5' : ''
                    }`}
                    aria-current="page"
                    onClick={() => handleLinkClick('home')}
                  >
                    ໜ້າຫຼັກ
                  </a>
                </li>
                <li>
                  <a
                    href="#InfractionTracker"
                    className={`block py-2 pl-3 pr-4 text-gray-900 dark:text-white rounded hover:bg-gray-100  ${
                      active === 'InfractionTracker'
                        ? 'font-bold bg-gray-200 p-5'
                        : ''
                    }`}
                    onClick={() => handleLinkClick('InfractionTracker')}
                  >
                    ລາຍງຍລົດທີ່ລ່ວງລະເມີດ
                  </a>
                </li>
                <li>
                  <a
                    href="#InfractionSearch"
                    className={`block py-2 pl-3 pr-4 p-5 text-gray-900 dark:text-white rounded hover:bg-gray-100  ${
                      active === 'InfractionSearch'
                        ? 'font-bold bg-gray-200 '
                        : ''
                    }`}
                    onClick={() => handleLinkClick('InfractionSearch')}
                  >
                    ຄົ້ນຫາລົດທີ່ລ່ວງລະເມີດ
                  </a>
                </li>
              </ul>
            </div>
          </nav>
        </header>
        <main className="w-full  mt-5  ">
          <div className=" text-center text-4xl my-10">Video Traffic Analytic Webapp</div>
          <header className=" space-y-10 mb-10">{children}</header>
        </main>
      </div>
    </>
  );
};
