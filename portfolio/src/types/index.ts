export type Stage = 'landing' | 'boot' | 'hud' | 'intro' | 'skills' | 'projects' | 'modal' | 'terminal' | 'chat' | 'contact';

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
}

export interface StageContextType {
  currentStage: Stage;
  setStage: (stage: Stage) => void;
  isTransitioning: boolean;
  modalProject: Project | null;
  openModal: (project: Project) => void;
  closeModal: () => void;
}
