import React, { useState } from 'react';
import { useStage } from '../../context/useStage';
import { SKILLS, CERTIFICATIONS } from '../../data/projects';
import styles from './Skills.module.css';

interface Certification {
  id: string;
  name: string;
  provider: string;
  detail: string;
}

const Skills: React.FC = () => {
  const { isTransitioning } = useStage();
  const [selectedSkill, setSelectedSkill] = useState<{ id: string; name: string; detail: string } | null>(null);
  const [selectedCert, setSelectedCert] = useState<Certification | null>(null);

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
              <span className={styles.certDetailText}> — {selectedCert.detail}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Skills;
