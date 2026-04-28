import { useContext } from 'react';
import { StageContext } from './StageContext';

export const useStage = () => {
  const context = useContext(StageContext);
  if (context === undefined) {
    throw new Error('useStage must be used within a StageProvider');
  }
  return context;
};
