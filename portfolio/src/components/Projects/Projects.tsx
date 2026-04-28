import React, { useState } from 'react';
import styles from './Projects.module.css';

interface Project {
  id: string;
  title: string;
  description: string;
  tech: string[];
  year: string;
}

const PROJECTS_DATA: Project[] = [
  {
    id: '01',
    title: 'Flux OS',
    description: 'A fully functional browser-based OS interface with drag-and-drop window manager and virtual filesystem.',
    tech: ['React', 'TypeScript', 'Canvas API'],
    year: '2024'
  },
  {
    id: '02',
    title: 'SMART-SEARCH',
    description: 'Natural language file system search tool with zero-configuration semantic understanding.',
    tech: ['Python', 'RAG', 'Vector DB'],
    year: '2024'
  },
  {
    id: '03',
    title: 'LaRa',
    description: 'Low-cost AI therapy companion for specially-abled children with an offline-capable pipeline.',
    tech: ['PyTorch', 'Robotics', 'CV'],
    year: '2023'
  },
  {
    id: '04',
    title: 'ISL Recognition',
    description: 'Real-time Indian Sign Language recognition using CNNs with 99.8% accuracy at 45 FPS.',
    tech: ['TensorFlow', 'OpenCV', 'CNN'],
    year: '2023'
  },
  {
    id: '05',
    title: 'Signal',
    description: 'Real-time analytics dashboard with high-density data visualization and predictive modeling.',
    tech: ['D3.js', 'Next.js', 'Node.js'],
    year: '2023'
  }
];

const Projects: React.FC = () => {
  const [showAll, setShowAll] = useState(false);

  const displayedProjects = showAll ? PROJECTS_DATA : PROJECTS_DATA.slice(0, 3);

  return (
    <div className={styles.container}>
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
              onClick={() => {
                // Future: Open Modal (Stage 7)
                console.log(`Open ${project.title}`);
              }}
            >
              <div className={styles.cardHeader}>
                <span className={styles.projectId}>{project.id}</span>
                <span className={styles.projectYear}>{project.year}</span>
              </div>
              
              <h3 className={`${styles.projectTitle} syne`}>{project.title}</h3>
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
              <span className={styles.plus}>+</span> EXPAND PROJECTS
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Projects;
