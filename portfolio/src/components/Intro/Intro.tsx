import React from 'react';
import { useStage } from '../../context/useStage';
import { PROFILE, EDUCATION } from '../../data/projects';
import styles from './Intro.module.css';

const Intro: React.FC = () => {
  const { setStage, isTransitioning } = useStage();

  return (
    <div className={`${styles.container} ${isTransitioning ? styles.exiting : ''}`}>
      <div className={styles.content}>
        <div className={styles.statusLine}>
          <span className={styles.accentText}>//</span> Available for work
        </div>
        
        <h1 className={`${styles.name} syne`}>
          {PROFILE.name.split('\n').map((line, i) => (
            <React.Fragment key={i}>
              {line}
              {i < PROFILE.name.split('\n').length - 1 && <br />}
            </React.Fragment>
          ))}
        </h1>
        
        <div className={styles.roleLine}>
          {PROFILE.roles.map((role, i) => (
            <React.Fragment key={role}>
              {role}
              {i < PROFILE.roles.length - 1 && <span className={styles.dot}>·</span>}
            </React.Fragment>
          ))}
          <div className={styles.cursor} />
        </div>
        
        <p className={styles.description}>{PROFILE.summary}</p>

        <div className={styles.education}>
          <span className={styles.eduDegree}>{EDUCATION.degree}</span>
          <span className={styles.eduDot}>·</span>
          <span className={styles.eduSchool}>{EDUCATION.school}</span>
          <span className={styles.eduDot}>·</span>
          <span className={styles.eduCgpa}>CGPA: {EDUCATION.cgpa} / 10</span>
          <span className={styles.eduDot}>·</span>
          <span className={styles.eduYear}>{EDUCATION.year}</span>
        </div>
        
        <div className={styles.navPills}>
          <button className={styles.pill} onClick={() => setStage('skills')}>Skills</button>
          <button className={styles.pill} onClick={() => setStage('projects')}>Projects</button>
          <button className={styles.pill} onClick={() => setStage('achievements')}>Achievements</button>
          <button className={styles.pill} onClick={() => setStage('contact')}>Contact</button>
        </div>
      </div>
    </div>
  );
};

export default Intro;
