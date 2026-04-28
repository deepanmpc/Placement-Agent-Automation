import React, { useState } from 'react';
import { useStage } from '../../context/useStage';
import { PROJECTS_DATA, ACHIEVEMENTS } from '../../data/projects';
import styles from './Projects.module.css';

const Projects: React.FC = () => {
  const { isTransitioning, openModal } = useStage();
  const [showAll, setShowAll] = useState(false);

  const displayedProjects = showAll ? PROJECTS_DATA : PROJECTS_DATA.slice(0, 3);

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
          <ul className={styles.achievementsList}>
            {ACHIEVEMENTS.map((achievement, idx) => (
              <li 
                key={achievement.id} 
                className={styles.achievementItem}
                style={{ animationDelay: `${(PROJECTS_DATA.length + idx) * 80}ms` }}
              >
                <span className={styles.achievementPrefix}>›</span>
                <span className={styles.achievementText}>{achievement.text}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Projects;
