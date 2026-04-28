import React from 'react';
import { useStage } from '../../context/useStage';
import styles from './Intro.module.css';

const EDUCATION_DATA = {
  degree: 'B.Tech Computer Science',
  school: 'Vellore Institute of Technology',
  years: '2022 — 2026',
  year: '3rd Year',
};

const Intro: React.FC = () => {
  const { setStage, isTransitioning } = useStage();

  return (
    <div className={`${styles.container} ${isTransitioning ? styles.exiting : ''}`}>
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

        {/* 5. Education */}
        <div className={styles.education}>
          <span className={styles.eduDegree}>{EDUCATION_DATA.degree}</span>
          <span className={styles.eduDot}>·</span>
          <span className={styles.eduSchool}>{EDUCATION_DATA.school}</span>
          <span className={styles.eduDot}>·</span>
          <span className={styles.eduYear}>{EDUCATION_DATA.year}</span>
        </div>
        
        {/* 6. Nav Pills */}
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
