import React, { useState } from 'react';
import { useStage } from '../../context/useStage';
import { PROFILE, EDUCATION, ACHIEVEMENTS, PROJECTS_DATA } from '../../data/projects';
import type { Project } from '../../types';
import styles from './Intro.module.css';

const Intro: React.FC = () => {
  const { setStage, isTransitioning, openModal } = useStage();
  const [showAchievements, setShowAchievements] = useState(false);

  const getProjectForAchievement = (achievementText: string): Project | undefined => {
    const text = achievementText.toLowerCase();
    if (text.includes('rampage') || text.includes('neurodott')) return PROJECTS_DATA.find(p => p.title === 'NeuroDott');
    if (text.includes('3d') || text.includes('apparel')) return PROJECTS_DATA.find(p => p.title === '3D Apparel Customizer');
    if (text.includes('search') || text.includes('wizard')) return PROJECTS_DATA.find(p => p.title === 'Search Wizard');
    return undefined;
  };

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
          <button className={styles.pill} onClick={() => setStage('contact')}>Contact</button>
          <button className={styles.pill} onClick={() => setShowAchievements(!showAchievements)}>
            Achievements
          </button>
        </div>

        {showAchievements && (
          <div className={styles.achievementsSection}>
            <div className={styles.achievementsGrid}>
              {ACHIEVEMENTS.map((achievement, idx) => {
                const linkedProject = getProjectForAchievement(achievement.text);
                return (
                  <div 
                    key={achievement.id} 
                    className={`${styles.achievementCard} ${linkedProject ? styles.clickable : ''}`}
                    style={{ animationDelay: `${idx * 80}ms` }}
                    onClick={() => linkedProject && openModal(linkedProject)}
                  >
                    <div className={styles.achievementCardHeader}>
                      <span className={styles.achievementIcon}>★</span>
                      <span className={styles.achievementProject}>{linkedProject?.title || '—'}</span>
                    </div>
                    <p className={styles.achievementCardText}>{achievement.text}</p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Intro;
