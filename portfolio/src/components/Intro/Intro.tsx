import React from 'react';
import { useStage } from '../../context/useStage';
import styles from './Intro.module.css';

const Intro: React.FC = () => {
  const { setStage } = useStage();

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        {/* 1. Status Line */}
        <div className={styles.statusLine}>
          <span className={styles.accentText}>//</span> Currently available for work
        </div>
        
        {/* 2. Name */}
        <h1 className={`${styles.name} syne`}>
          Deepan<br />
          Chandrasekaran.
        </h1>
        
        {/* 3. Role Line + Cursor */}
        <div className={styles.roleLine}>
          AI Engineer <span className={styles.dot}>·</span> Full-Stack Developer <span className={styles.dot}>·</span> Researcher
          <div className={styles.cursor} />
        </div>
        
        {/* 4. Description */}
        <p className={styles.description}>
          I build semantic systems and AI-human interfaces,<br />
          from low-cost therapy companions to spatial systems.
        </p>

        {/* 5. Nav Pills */}
        <div className={styles.navPills}>
          <button className={styles.pill} onClick={() => setStage('skills')}>Skills</button>
          <button className={styles.pill} onClick={() => setStage('projects')}>Projects</button>
          <button className={styles.pill} onClick={() => setStage('contact')}>Contact</button>
        </div>
      </div>
    </div>
  );
};

export default Intro;
