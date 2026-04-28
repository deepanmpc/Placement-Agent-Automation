import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useStage } from '../../context/useStage';
import styles from './Boot.module.css';

const BOOT_LINES = [
  "Loading modules...",
  "Initializing interface...",
  "Mounting scene graph...",
  "System ready."
];

const TypewriterLine: React.FC<{ 
  text: string, 
  isActive: boolean, 
  isSkipped: boolean, 
  isLast: boolean,
  onComplete?: () => void 
}> = ({ text, isActive, isSkipped, isLast, onComplete }) => {
  const [displayedText, setDisplayedText] = useState(isSkipped ? text : '');
  const [isTyping, setIsTyping] = useState(false);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    if (isSkipped) {
      setDisplayedText(text);
      return;
    }

    if (isActive && !isTyping && displayedText.length < text.length) {
      setIsTyping(true);
      let i = displayedText.length;
      const charDelay = 20;
      
      const type = () => {
        if (i < text.length) {
          setDisplayedText(text.substring(0, i + 1));
          i++;
          timerRef.current = window.setTimeout(type, charDelay);
        } else {
          setIsTyping(false);
          if (onComplete) onComplete();
        }
      };
      
      type();
    }

    return () => {
      if (timerRef.current) window.clearTimeout(timerRef.current);
    };
  }, [isActive, text, isSkipped, isTyping, onComplete]);

  const showCursor = isActive || (isLast && isSkipped);

  return (
    <div className={`${styles.line} ${isActive || displayedText.length > 0 ? styles.lineVisible : ''} ${isActive ? styles.lineActive : ''}`}>
      <span className={styles.prefix}>›</span>
      <span className={styles.text}>{displayedText}</span>
      {showCursor && <div className={isLast ? styles.cursor : styles.cursorSmall} />}
    </div>
  );
};

const Boot: React.FC = () => {
  const { setStage } = useStage();
  const [activeIndex, setActiveIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [isSkipped, setIsSkipped] = useState(false);
  const [isExiting, setIsExiting] = useState(false);
  const exitTimeoutRef = useRef<number | null>(null);

  const completeBoot = useCallback(() => {
    if (isComplete) return;
    setIsComplete(true);
    
    exitTimeoutRef.current = window.setTimeout(() => {
      setIsExiting(true);
      window.setTimeout(() => {
        setStage('intro');
      }, 400);
    }, 200);
  }, [isComplete, setStage]);

  const handleSkip = useCallback(() => {
    if (isComplete) return;
    setIsSkipped(true);
    setActiveIndex(BOOT_LINES.length - 1);
    completeBoot();
  }, [isComplete, completeBoot]);

  useEffect(() => {
    window.addEventListener('keydown', handleSkip);
    window.addEventListener('click', handleSkip);

    return () => {
      window.removeEventListener('keydown', handleSkip);
      window.removeEventListener('click', handleSkip);
      if (exitTimeoutRef.current) clearTimeout(exitTimeoutRef.current);
    };
  }, [handleSkip]);

  const onLineComplete = () => {
    if (activeIndex < BOOT_LINES.length - 1) {
      setTimeout(() => {
        setActiveIndex(prev => prev + 1);
      }, 100);
    } else {
      completeBoot();
    }
  };

  return (
    <div className={`${styles.container} ${isExiting ? styles.exiting : ''}`}>
      <div className={styles.bootBox}>
        <div className={styles.logs}>
          {BOOT_LINES.map((line, index) => (
            <TypewriterLine 
              key={index}
              text={line}
              isActive={index === activeIndex && !isComplete}
              isSkipped={isSkipped || (isComplete && index <= activeIndex)}
              isLast={index === BOOT_LINES.length - 1}
              onComplete={index === activeIndex ? onLineComplete : undefined}
            />
          ))}
        </div>
        
        <div className={styles.progressContainer}>
          <div 
            className={styles.progressBar} 
            style={{ 
              width: isComplete ? '100%' : `${((activeIndex + 1) / BOOT_LINES.length) * 100}%`,
              transition: isSkipped ? 'none' : `width 0.3s ease-out`
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default Boot;
