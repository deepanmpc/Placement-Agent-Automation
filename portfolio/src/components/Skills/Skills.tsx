import React, { useState } from 'react';
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

const Skills: React.FC = () => {
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);

  return (
    <div className={styles.container}>
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
      </div>
    </div>
  );
};

export default Skills;
