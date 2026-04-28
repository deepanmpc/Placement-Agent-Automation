import React from 'react';
import styles from './Intro.module.css';

const Intro: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div className={styles.availability}>
          <span className={styles.dim}>//</span> Currently available for work
          <span className={styles.typingCursor} />
        </div>
        
        <h1 className={`${styles.name} syne`}>
          Deepan<br />
          Chandrasekaran.
        </h1>
        
        <div className={styles.role}>
          CS + AI Engineer <span className={styles.dot}>·</span> Full-Stack Developer <span className={styles.dot}>·</span> Robotic-AI Researcher
        </div>
        
        <p className={styles.tagline}>
          I engineer semantic systems and AI-human interfaces — from low-cost therapy companions to spatial file systems.
        </p>

        <div className={styles.actions}>
          <button className={styles.btn}>Skills</button>
          <button className={styles.btn}>Projects</button>
          <button className={styles.btn}>Contact</button>
        </div>
      </div>
    </div>
  );
};

export default Intro;
