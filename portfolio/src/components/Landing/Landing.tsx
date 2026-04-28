import React, { useEffect, useState, useCallback } from 'react';
import { useStage } from '../../context/useStage';
import styles from './Landing.module.css';

const Landing: React.FC = () => {
  const { setStage, isTransitioning } = useStage();
  const [isInitialized, setIsInitialized] = useState(false);

  const handleInitialize = useCallback(() => {
    if (isInitialized) return;
    setIsInitialized(true);
    setStage('boot');
  }, [isInitialized, setStage]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter') {
        handleInitialize();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleInitialize]);

  return (
    <div 
      className={`${styles.container} ${isTransitioning ? styles.exiting : ''}`}
      onClick={handleInitialize}
    >
      <div className={styles.content}>
        <div className={styles.systemLabel}>SYS://PORTFOLIO — v2.4.1</div>
        
        <h1 className={`${styles.headline} syne`}>
          A designer who<br />
          engineers <span className="ac">experiences.</span>
        </h1>

        <div className={styles.cta}>
          <div className={styles.accentBar} />
          <span className={styles.ctaText}>INITIALIZE SYSTEM</span>
          <div className={styles.cursor} />
        </div>
      </div>
    </div>
  );
};

export default Landing;
