import React, { useState } from 'react';
import type { ReactNode } from 'react';
import type { Stage } from '../types';
import { StageContext } from './StageContext';

export const StageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentStage, setCurrentStage] = useState<Stage>('landing');
  const [isTransitioning, setIsTransitioning] = useState(false);

  const setStage = (newStage: Stage) => {
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentStage(newStage);
      setIsTransitioning(false);
    }, 500);
  };

  return (
    <StageContext.Provider value={{ currentStage, setStage, isTransitioning }}>
      {children}
    </StageContext.Provider>
  );
};
