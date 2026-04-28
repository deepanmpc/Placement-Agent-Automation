import { createContext } from 'react';
import type { StageContextType } from '../types';

export const StageContext = createContext<StageContextType | undefined>(undefined);
