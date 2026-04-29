export type Stage = 'landing' | 'boot' | 'hud' | 'intro' | 'skills' | 'projects' | 'achievements' | 'modal' | 'terminal' | 'chat' | 'contact';

export interface Project {
  id: string;
  displayId: string;
  title: string;
  description: string;
  problem?: string;
  solution?: string;
  impact?: string;
  tech: string[];
  year: string;
  link?: string;
  repo?: string;
}

export interface StageContextType {
  currentStage: Stage;
  setStage: (stage: Stage) => void;
  canGoBack: boolean;
  goBack: () => void;
  isTransitioning: boolean;
  modalProject: Project | null;
  openModal: (project: Project) => void;
  closeModal: () => void;
  isTerminalOpen: boolean;
  openTerminal: () => void;
  closeTerminal: () => void;
  toggleTerminal: () => void;
  isChatOpen: boolean;
  openChat: () => void;
  closeChat: () => void;
  closeAll: () => void;
  isAnyOverlayOpen: boolean;
}
