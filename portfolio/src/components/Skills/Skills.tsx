import React, { useState } from 'react';
import { useStage } from '../../context/useStage';
import styles from './Skills.module.css';

interface Skill {
  id: string;
  name: string;
  detail: string;
}

const SKILLS_DATA: Skill[] = [
  { id: '1', name: 'React / Next.js', detail: 'Building production-grade systems with focus on performance, DX, and scalable architectures.' },
  { id: '2', name: 'AI / ML Engineering', detail: 'Developing RAG architectures, CV pipelines (99.8% ISL accuracy), and offline AI therapy companions.' },
  { id: '3', name: 'TypeScript / Node.js', detail: 'Architecting type-safe full-stack applications and high-performance backend APIs.' },
  { id: '4', name: 'Robotic-AI / CV', detail: 'Researching low-cost human-machine interfaces and real-time computer vision processing.' },
  { id: '5', name: 'Systems Design', detail: 'Engineering semantic file systems and modular software architectures for the next computing era.' },
  { id: '6', name: 'Python / Data Science', detail: 'Leveraging data-driven insights and advanced ML models for complex problem solving.' },
];

interface Certification {
  id: string;
  name: string;
  provider: string;
  detail: string;
}

const CERTIFICATIONS_DATA: Certification[] = [
  { id: 's9d2mz', name: 'Google ML Certificate', provider: 'Coursera', detail: 'Machine LearningSpecialization' },
  { id: 'c8k3w1', name: 'AWS Cloud Practitioner', provider: 'Amazon', detail: 'Cloud Fundamentals' },
  { id: '9m2zlr', name: 'Deep Learning Specialization', provider: 'Andrew Ng', detail: 'Neural Networks & Deep Learning' },
];

const Skills: React.FC = () => {
  const { isTransitioning } = useStage();
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [selectedCert, setSelectedCert] = useState<Certification | null>(null);

  return (
    <div className={`${styles.container} ${isTransitioning ? styles.exiting : ''}`}>
      <div className={styles.content}>
        <div className={styles.label}>
          <span className={styles.accentDot}>•</span> SKILLS
        </div>
        
        <div className={styles.skillsGrid}>
          {SKILLS_DATA.map((skill, idx) => (
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
            {CERTIFICATIONS_DATA.map((cert, idx) => (
              <div 
                key={cert.id}
                className={`${styles.certBlock} ${selectedCert?.id === cert.id ? styles.active : ''}`}
                style={{ animationDelay: `${(idx + SKILLS_DATA.length) * 60}ms` }}
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
