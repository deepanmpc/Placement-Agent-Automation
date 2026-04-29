import React from 'react';
import { useStage } from '../../context/useStage';
import { ACHIEVEMENTS, PROJECTS_DATA } from '../../data/projects';
import type { Project } from '../../types';
import styles from './Achievements.module.css';

const Achievements: React.FC = () => {
  const { isTransitioning, openModal } = useStage();

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
        <div className={styles.label}>
          <span className={styles.accentDot}>•</span> ACHIEVEMENTS
        </div>

        <div className={styles.grid}>
          {ACHIEVEMENTS.map((achievement, idx) => {
            const linkedProject = getProjectForAchievement(achievement.text);
            return (
              <div 
                key={achievement.id} 
                className={`${styles.card} ${linkedProject ? styles.clickable : ''}`}
                style={{ animationDelay: `${idx * 120}ms` }}
                onClick={() => linkedProject && openModal(linkedProject)}
              >
                <div className={styles.cardHeader}>
                  <span className={styles.icon}>★</span>
                  <span className={styles.projectTag}>{linkedProject?.title || '—'}</span>
                </div>
                
                <h3 className={styles.title}>{achievement.text}</h3>
                
                <div className={styles.cardBorder} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Achievements;