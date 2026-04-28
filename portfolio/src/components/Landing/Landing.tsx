import React, { useEffect, useState, useCallback } from 'react';
import { useStage } from '../../context/useStage';
import styles from './Landing.module.css';

const Landing: React.FC = () => {
  const { setStage, isTransitioning } = useStage();
  const [isInitialized, setIsInitialized] = useState(false);
  const [isActivating, setIsActivating] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [showHint, setShowHint] = useState(false);

  const handleInitialize = useCallback(() => {
    if (isInitialized || isActivating) return;
    
    setIsActivating(true);
    
    // Brief highlight/pause before transitioning
    setTimeout(() => {
      setIsInitialized(true);
      setStage('boot');
    }, 150);
  }, [isInitialized, isActivating, setStage]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter') {
        handleInitialize();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleInitialize]);

  // Instructions and Hint timers
  useEffect(() => {
    const instructionTimer = setTimeout(() => {
      setShowInstructions(true);
    }, 1000);

    const hintTimer = setTimeout(() => {
      if (!isInitialized && !isActivating) {
        setShowHint(true);
        // Hide hint after 2 seconds
        setTimeout(() => setShowHint(false), 2000);
      }
    }, 4500);

    return () => {
      clearTimeout(instructionTimer);
      clearTimeout(hintTimer);
    };
  }, [isInitialized, isActivating]);

  return (
    <div className={`${styles.container} ${isTransitioning ? styles.exiting : ''}`}>
      <div className={styles.content}>
        <div className={styles.systemLabel}>SYS://DEEPAN — v4.0.1_RAG</div>
        
        <h1 className={`${styles.headline} syne`}>
          An engineer who<br />
          architects <span className="ac">intelligence.</span>
        </h1>

        <div className={styles.ctaWrapper}>
          <div 
            className={`${styles.cta} ${isActivating ? styles.ctaActive : ''}`}
            onClick={handleInitialize}
          >
            <div className={styles.accentBar} />
            <span className={styles.ctaText}>INITIALIZE SYSTEM</span>
            <div className={`${styles.cursor} ${isActivating ? styles.cursorStopped : ''}`} />
          </div>
          
          <div className={`${styles.instructions} ${showInstructions ? styles.visible : ''}`}>
            Press Enter or click to begin
          </div>

          <div className={`${styles.hint} ${showHint ? styles.visible : ''}`}>
            Try pressing Enter
          </div>
        </div>
      </div>
    </div>
  );
};

export default Landing;
