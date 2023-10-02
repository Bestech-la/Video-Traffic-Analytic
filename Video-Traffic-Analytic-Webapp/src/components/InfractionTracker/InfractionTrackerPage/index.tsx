import React from 'react';
import { InfractionTrackerList } from '../List';

export const InfractionTrackerPage: React.FC<any> = ({}) => {
  return (
    <section id="InfractionTracker">
      <div className="w-3/4 mx-auto">
        <InfractionTrackerList />
      </div>
    </section>
  );
};
