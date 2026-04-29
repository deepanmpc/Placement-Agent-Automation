import React, { useState } from 'react';
import { useStage } from '../../context/useStage';
import { PROJECTS_DATA } from '../../data/projects';
import styles from './Projects.module.css';

const Projects: React.FC = () => {
  const { isTransitioning, openModal } = useStage();
  const [showAll, setShowAll] = useState(false);

  const mainProjects = PROJECTS_DATA.filter(p => !p.displayId.startsWith('OSS'));
  const openSource = PROJECTS_DATA.filter(p => p.displayId.startsWith('OSS'));

  const displayedProjects = showAll ? mainProjects : mainProjects.slice(0, 3);

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

        {mainProjects.length > 3 && (
          <div className={styles.expandWrapper}>
            <button 
              className={styles.expandBtn}
              onClick={() => setShowAll(!showAll)}
            >
              <span className={styles.plus}>{showAll ? '-' : '+'}</span> {showAll ? 'SHOW LESS' : 'EXPLORE MORE'}
            </button>
          </div>
        )}

        <div className={styles.openSourceSection}>
          <div className={styles.label}>
            <span className={styles.accentDot}>•</span> OPEN SOURCE WORKS
          </div>

          <div className={styles.grid}>
            {openSource.map((project, idx) => (
              <div 
                key={project.id} 
                className={styles.card}
                style={{ animationDelay: `${(mainProjects.length + idx) * 120}ms` }}
                onClick={() => openModal(project)}
              >
                <div className={styles.cardHeader}>
                  <span className={styles.projectId}>OPEN SOURCE</span>
                  <span className={styles.projectYear}>{project.year}</span>
                </div>
                
                <h3 className={`${styles.projectTitle} syne`}>
                  <span className={styles.num}>OSS — </span>
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
        </div>
      </div>
    </div>
  );
};

export default Projects;
