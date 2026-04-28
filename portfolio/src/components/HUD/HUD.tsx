import React, { useEffect, useState } from 'react';
import { useStage } from '../../context/useStage';
import styles from './HUD.module.css';

const SECTIONS = ['INTRO', 'SKILLS', 'PROJECTS', 'CONTACT'];

const HUD: React.FC = () => {
  const { currentStage, setStage } = useStage();
  const [isActivated, setIsActivated] = useState(false);
  const [visibleDots, setVisibleDots] = useState<number>(0);
  const [showLabel, setShowLabel] = useState(false);
  const [showCoords, setShowCoords] = useState(false);

  // Activation sequence for Stage 3
  useEffect(() => {
    if (currentStage === 'hud' && !isActivated) {
      // Step 1: Label
      setShowLabel(true);

      // Step 2: Coordinates (120ms delay)
      const coordsTimer = setTimeout(() => {
        setShowCoords(true);
      }, 120);

      // Step 3: Nav Dots (200ms after coordinates, 80ms stagger)
      const dotsStartTimer = setTimeout(() => {
        let dotsShown = 0;
        const staggerInterval = setInterval(() => {
          dotsShown++;
          setVisibleDots(dotsShown);
          if (dotsShown >= SECTIONS.length) {
            clearInterval(staggerInterval);
            // Sequence complete
            setIsActivated(true);
            // Transition to Stage 4 (Intro) after a tiny pause
            setTimeout(() => setStage('intro'), 300);
          }
        }, 80);
      }, 320); // 120ms + 200ms

      return () => {
        clearTimeout(coordsTimer);
        clearTimeout(dotsStartTimer);
      };
    }
  }, [currentStage, isActivated, setStage]);

  // Don't render HUD before Stage 3
  if (currentStage === 'landing' || currentStage === 'boot') return null;

  const displaySection = currentStage === 'hud' ? 'INTRO' : currentStage.toUpperCase();

  return (
    <div className={styles.container}>
      {/* Top HUD Label */}
      <div className={`${styles.topHUD} ${showLabel ? styles.active : ''}`}>
        <div className={styles.accentDot} />
        <span className={styles.sectionLabel}>SYS://{displaySection}_DEEPAN</span>
      </div>

      {/* Bottom Coordinates */}
      <div className={`${styles.bottomHUD} ${showCoords ? styles.active : ''}`}>
        <span className={styles.coords}>12.3401°N 77.2901°E</span>
      </div>

      {/* Right Navigation Dots */}
      <div className={styles.rightNav}>
        {SECTIONS.map((section, idx) => (
          <div 
            key={section}
            className={`
              ${styles.navDot} 
              ${idx < visibleDots ? styles.dotVisible : ''} 
              ${displaySection === section ? styles.dotActive : ''}
            `}
            title={section}
          />
        ))}
      </div>
    </div>
  );
};

export default HUD;
