import React, { useCallback, useState } from 'react';
import type { ReactNode } from 'react';
import type { Stage, Project } from '../types';
import { StageContext } from './StageContext';

const HISTORY_STAGES: Stage[] = ['intro', 'skills', 'projects', 'contact'];

export const StageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentStage, setCurrentStage] = useState<Stage>('landing');
  const [stageHistory, setStageHistory] = useState<Stage[]>([]);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [modalProject, setModalProject] = useState<Project | null>(null);
  const [isTerminalOpen, setIsTerminalOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  const setStage = useCallback((newStage: Stage) => {
    if (newStage === currentStage) return;

    setIsTransitioning(true);
    setTimeout(() => {
      if (HISTORY_STAGES.includes(currentStage)) {
        setStageHistory((history) => [...history, currentStage].slice(-12));
      }
      setCurrentStage(newStage);
      setIsTransitioning(false);
    }, 500);
  }, [currentStage]);

  const goBack = useCallback(() => {
    setStageHistory((history) => {
      const previousStage = history.at(-1);
      if (!previousStage) return history;

      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentStage(previousStage);
        setIsTransitioning(false);
      }, 300);

      return history.slice(0, -1);
    });
  }, []);

  const openModal = (project: Project) => {
    setIsTerminalOpen(false);
    setIsChatOpen(false);
    setModalProject(project);
  };

  const closeModal = () => {
    setModalProject(null);
    setIsTerminalOpen(false);
    setIsChatOpen(false);
  };

  const openTerminal = () => {
    setModalProject(null);
    setIsChatOpen(false);
    setIsTerminalOpen(true);
  };

  const closeTerminal = () => {
    setIsTerminalOpen(false);
  };

  const toggleTerminal = () => {
    setIsTerminalOpen((isOpen) => {
      if (!isOpen) {
        setModalProject(null);
        setIsChatOpen(false);
      }
      return !isOpen;
    });
  };

  const openChat = () => {
    setModalProject(null);
    setIsTerminalOpen(false);
    setIsChatOpen(true);
  };

  const closeChat = () => {
    setIsChatOpen(false);
  };

  const closeAll = () => {
    setModalProject(null);
    setIsTerminalOpen(false);
    setIsChatOpen(false);
  };

  const isAnyOverlayOpen = Boolean(modalProject) || isTerminalOpen || isChatOpen;

  return (
    <StageContext.Provider value={{ 
      currentStage, 
      setStage, 
      canGoBack: stageHistory.length > 0,
      goBack,
      isTransitioning, 
      modalProject, 
      openModal, 
      closeModal,
      isTerminalOpen,
      openTerminal,
      closeTerminal,
      toggleTerminal,
      isChatOpen,
      openChat,
      closeChat,
      closeAll,
      isAnyOverlayOpen
    }}>
      {children}
    </StageContext.Provider>
  );
};
