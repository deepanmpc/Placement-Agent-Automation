export type Stage = 'landing' | 'boot' | 'intro' | 'hud' | 'projects' | 'modal' | 'terminal' | 'chat' | 'contact';

export interface StageContextType {
  currentStage: Stage;
  setStage: (stage: Stage) => void;
  isTransitioning: boolean;
}
