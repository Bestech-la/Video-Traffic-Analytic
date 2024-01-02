/* eslint-disable no-unused-vars */
/* eslint-disable @typescript-eslint/no-unused-vars */
import { Navbar } from '@components/Nav';
import { InfractionTrackerPage } from '@components/InfractionTracker/InfractionTrackerPage';
import { InfractionSearchPage } from '@components/InfractionSearch/InfractionSearchPage';
import React from 'react';
import { type GetServerSideProps } from 'next';
import { VideoLayout }  from '@components/Videos/VideoLayout';

const Landing: React.FC = () => {
  return (
    <Navbar>
      <VideoLayout/>
      <InfractionTrackerPage />
      {/* <InfractionSearchPage /> */}
    </Navbar>
  );
};

export default Landing;

export const getServerSideProps: GetServerSideProps = async (context) => {
  try {
    return {
      props: {},
    };
  } catch (error) {
    return {
      redirect: {
        destination: '/',
        permanent: false,
      },
    };
  }
};
