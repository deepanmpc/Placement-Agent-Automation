import React, { useState } from 'react';
import { useStage } from '../../context/useStage';
import { PROJECTS_DATA, SKILLS, CERTIFICATIONS } from '../../data/projects';
import styles from './Skills.module.css';

const Skills: React.FC = () => {
  const { isTransitioning, openModal } = useStage();
  const [selectedSkill, setSelectedSkill] = useState<{ id: string; name: string; detail: string; projects: string[] } | null>(null);
  const [selectedCert, setSelectedCert] = useState<{ id: string; name: string; provider: string; year: string } | null>(null);

  const handleProjectClick = (projectTitle: string) => {
    const project = PROJECTS_DATA.find(p => p.title === projectTitle);
    if (project) {
      openModal(project);
    }
  };

  return (
    <div className={`${styles.container} ${isTransitioning ? styles.exiting : ''}`}>
      <div className={styles.content}>
        <div className={styles.label}>
          <span className={styles.accentDot}>•</span> SKILLS
        </div>
        
        <div className={styles.skillsGrid}>
          {SKILLS.map((skill, idx) => (
            <div 
              key={skill.id}
              className={`${styles.skillBlock} ${selectedSkill?.id === skill.id ? styles.active : ''}`}
              style={{ animationDelay: `${idx * 80}ms` }}
              onClick={() => setSelectedSkill(skill)}
            >
              <span className={styles.skillName}>[ {skill.name} ]</span>
            </div>
          ))}
        </div>

        {selectedSkill && (
          <div className={styles.detailPanel} key={selectedSkill.id}>
            <span className={styles.prefix}>›</span>
            <p className={styles.detailText}>{selectedSkill.detail}</p>
            <div className={styles.usedIn}>
              <span className={styles.usedInLabel}>Used in:</span>
              {selectedSkill.projects.map((proj, idx) => (
                <button
                  key={proj}
                  className={styles.projectLink}
                  onClick={(e) => { e.stopPropagation(); handleProjectClick(proj); }}
                >
                  {proj}{idx < selectedSkill.projects.length - 1 ? ', ' : ''}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className={styles.certSection}>
          <div className={styles.certLabel}>
            <span className={styles.accentDot}>•</span> CERTIFICATIONS
          </div>
          <div className={styles.certGrid}>
            {CERTIFICATIONS.map((cert, idx) => (
              <div 
                key={cert.id}
                className={`${styles.certBlock} ${selectedCert?.id === cert.id ? styles.active : ''}`}
                style={{ animationDelay: `${(idx + SKILLS.length) * 60}ms` }}
                onClick={() => setSelectedCert(cert)}
              >
                <span className={styles.certName}>{cert.name}</span>
              </div>
            ))}
          </div>
          {selectedCert && (
            <div className={styles.certDetail} key={selectedCert.id}>
              <span className={styles.prefix}>›</span>
              <span className={styles.certProvider}>{selectedCert.provider}</span>
              <span className={styles.certDetailText}> — {selectedCert.year}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Skills;
