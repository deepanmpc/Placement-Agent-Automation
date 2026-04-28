import React, { useState } from 'react';
import { useStage } from '../../context/useStage';
import { PROJECTS_DATA, ACHIEVEMENTS } from '../../data/projects';
import type { Project } from '../../types';
import styles from './Projects.module.css';

const Projects: React.FC = () => {
  const { isTransitioning, openModal } = useStage();
  const [showAll, setShowAll] = useState(false);

  const displayedProjects = showAll ? PROJECTS_DATA : PROJECTS_DATA.slice(0, 3);

  const getProjectForAchievement = (achievementText: string): Project | undefined => {
    const text = achievementText.toLowerCase();
    if (text.includes('rampage') || text.includes('neurodott')) return PROJECTS_DATA.find(p => p.title === 'NeuroDott');
    if (text.includes('3d') || text.includes('apparel')) return PROJECTS_DATA.find(p => p.title === '3D Apparel Customizer');
    if (text.includes('search') || text.includes('wizard')) return PROJECTS_DATA.find(p => p.title === 'Search Wizard');
    return undefined;
  };

  const handleAchievementClick = (achievementText: string) => {
    const project = getProjectForAchievement(achievementText);
    if (project) openModal(project);
  };

  return (
    <div className={`${styles.container} ${isTransitioning ? styles.exiting : ''}`}>
      <div className={styles.content}>
        <div className={styles.label}>
          <span className={styles.accentDot}>•</span> PROJECTS
        </div>

        <div className={styles.grid}>
          {displayedProjects.map((project, idx) => (
            <div 
              key={project.id} 
              className={styles.card}
              style={{ animationDelay: `${idx * 120}ms` }}
              onClick={() => openModal(project)}
            >
              <div className={styles.cardHeader}>
                <span className={styles.projectId}>PROJECT {project.displayId}</span>
                <span className={styles.projectYear}>{project.year}</span>
              </div>
              
              <h3 className={`${styles.projectTitle} syne`}>
                <span className={styles.num}>{project.displayId} — </span>
                {project.title}
              </h3>
              <p className={styles.projectDesc}>{project.description}</p>
              
              <div className={styles.techStack}>
                {project.tech.map(t => (
                  <span key={t} className={styles.techTag}>{t}</span>
                ))}
              </div>
              
              <div className={styles.cardBorder} />
            </div>
          ))}
        </div>

        {!showAll && PROJECTS_DATA.length > 3 && (
          <div className={styles.expandWrapper}>
            <button 
              className={styles.expandBtn}
              onClick={() => setShowAll(true)}
            >
              <span className={styles.plus}>+</span> EXPLORE MORE SYSTEMS
            </button>
          </div>
        )}

        <div className={styles.achievements}>
          <div className={styles.achievementsLabel}>
            <span className={styles.accentDot}>•</span> ACHIEVEMENTS
          </div>
          <div className={styles.achievementsGrid}>
            {ACHIEVEMENTS.map((achievement, idx) => {
              const linkedProject = getProjectForAchievement(achievement.text);
              return (
                <div 
                  key={achievement.id} 
                  className={`${styles.achievementCard} ${linkedProject ? styles.clickable : ''}`}
                  style={{ animationDelay: `${(PROJECTS_DATA.length + idx) * 80}ms` }}
                  onClick={() => linkedProject && handleAchievementClick(achievement.text)}
                >
                  <div className={styles.achievementCardHeader}>
                    <span className={styles.achievementIcon}>★</span>
                    <span className={styles.achievementProject}>{linkedProject?.title || '���'}</span>
                  </div>
                  <p className={styles.achievementCardText}>{achievement.text}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Projects;
