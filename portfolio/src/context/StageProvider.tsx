import React, { useState } from 'react';
import type { ReactNode } from 'react';
import type { Stage, Project } from '../types';
import { StageContext } from './StageContext';

export const StageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentStage, setCurrentStage] = useState<Stage>('landing');
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [modalProject, setModalProject] = useState<Project | null>(null);

  const setStage = (newStage: Stage) => {
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentStage(newStage);
      setIsTransitioning(false);
    }, 500);
  };

  const openModal = (project: Project) => {
    setModalProject(project);
  };

  const closeModal = () => {
    setModalProject(null);
  };

  return (
    <StageContext.Provider value={{ 
      currentStage, 
      setStage, 
      isTransitioning, 
      modalProject, 
      openModal, 
      closeModal 
    }}>
      {children}
    </StageContext.Provider>
  );
};
