import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useStage } from '../../context/useStage';
import styles from './Boot.module.css';

const BOOT_LINES = [
  "Loading modules...",
  "Initializing interface...",
  "Mounting scene graph...",
  "System ready."
];

const Boot: React.FC = () => {
  const { setStage } = useStage();
  const [lineIndex, setLineIndex] = useState(0);
  const [displayedLines, setDisplayedLines] = useState<string[]>([]);
  const [currentText, setCurrentText] = useState("");
  const [isComplete, setIsComplete] = useState(false);
  const [isExiting, setIsExiting] = useState(false);
  
  const skipRef = useRef(false);

  const finishBoot = useCallback(() => {
    if (isComplete || isExiting) return;
    setIsComplete(true);
    
    // Slight pause after completion before transitioning
    setTimeout(() => {
      setIsExiting(true);
      setTimeout(() => {
        setStage('hud');
      }, 500); // Transition duration
    }, 400);
  }, [isComplete, isExiting, setStage]);

  const handleSkip = useCallback(() => {
    if (isComplete || isExiting) return;
    skipRef.current = true;
    setDisplayedLines(BOOT_LINES.slice(0, -1));
    setCurrentText(BOOT_LINES[BOOT_LINES.length - 1]);
    setLineIndex(BOOT_LINES.length - 1);
    finishBoot();
  }, [isComplete, isExiting, finishBoot]);

  useEffect(() => {
    if (isComplete || isExiting) return;

    const currentLineGoal = BOOT_LINES[lineIndex];
    
    if (currentText.length < currentLineGoal.length) {
      const timeout = setTimeout(() => {
        setCurrentText(currentLineGoal.slice(0, currentText.length + 1));
      }, 25); // Fast typing speed
      return () => clearTimeout(timeout);
    } else {
      // Line finished
      if (lineIndex < BOOT_LINES.length - 1) {
        const timeout = setTimeout(() => {
          setDisplayedLines(prev => [...prev, currentLineGoal]);
          setLineIndex(prev => prev + 1);
          setCurrentText("");
        }, 100); // Short pause between lines
        return () => clearTimeout(timeout);
      } else {
        finishBoot();
      }
    }
  }, [lineIndex, currentText, isComplete, isExiting, finishBoot]);

  useEffect(() => {
    const handleEvents = () => handleSkip();
    window.addEventListener('keydown', handleEvents);
    window.addEventListener('mousedown', handleEvents);
    
    return () => {
      window.removeEventListener('keydown', handleEvents);
      window.removeEventListener('mousedown', handleEvents);
    };
  }, [handleSkip]);

  const progress = isComplete ? 100 : ((lineIndex + (currentText.length / BOOT_LINES[lineIndex].length)) / BOOT_LINES.length) * 100;

  return (
    <div className={`${styles.container} ${isExiting ? styles.exiting : ''}`}>
      <div className={styles.content}>
        <div className={styles.logs}>
          {displayedLines.map((line, idx) => (
            <div key={idx} className={styles.line}>
              <span className={styles.prompt}>›</span>
              <span className={styles.text}>{line}</span>
              <span className={styles.check}>✓</span>
            </div>
          ))}
          {!isComplete || lineIndex === BOOT_LINES.length - 1 ? (
            <div className={`${styles.line} ${lineIndex === BOOT_LINES.length - 1 ? styles.finalLine : ''}`}>
              <span className={styles.prompt}>›</span>
              <span className={lineIndex === BOOT_LINES.length - 1 ? styles.activeText : styles.text}>
                {currentText}
              </span>
              {lineIndex === BOOT_LINES.length - 1 && (
                <div className={styles.cursor} />
              )}
            </div>
          ) : null}
        </div>
        
        <div className={styles.progressTrack}>
          <div 
            className={styles.progressBar} 
            style={{ width: `${progress}%` }} 
          />
        </div>

        <div className={styles.footer}>
          <span className={styles.meta}>SYS_INITIALIZE_v2.4.1</span>
          <span className={styles.meta}>EST_LOAD: ~2.0s</span>
        </div>
      </div>
    </div>
  );
};

export default Boot;
