export type Stage = 'landing' | 'boot' | 'hud' | 'intro' | 'skills' | 'projects' | 'modal' | 'terminal' | 'chat' | 'contact';

export interface StageContextType {
  currentStage: Stage;
  setStage: (stage: Stage) => void;
  isTransitioning: boolean;
}
