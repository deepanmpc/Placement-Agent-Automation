import React, { useState } from 'react';
import { useStage } from '../../context/useStage';
import styles from './Projects.module.css';

interface Project {
  id: string;
  displayId: string;
  title: string;
  description: string;
  tech: string[];
  year: string;
}

const PROJECTS_DATA: Project[] = [
  {
    id: 'bkw1f8',
    displayId: '001',
    title: 'SMART-SEARCH',
    description: 'Semantic file system search tool with zero-configuration natural language understanding.',
    tech: ['Python', 'RAG', 'Vector DB'],
    year: '2024'
  },
  {
    id: 'nj2m9x',
    displayId: '002',
    title: 'LaRa',
    description: 'Low-cost AI therapy companion for specially-abled children with an offline 4-layer pipeline.',
    tech: ['PyTorch', 'Robotics', 'CV'],
    year: '2023'
  },
  {
    id: 'x8y9z0',
    displayId: '003',
    title: 'ISL Recognition',
    description: 'Real-time Indian Sign Language recognition system achieving 99.8% accuracy for accessibility.',
    tech: ['TensorFlow', 'OpenCV', 'CNN'],
    year: '2023'
  },
  {
    id: 'p1q2r3',
    displayId: '004',
    title: 'Flux OS',
    description: 'Browser-based operating system interface with a custom window manager and virtual filesystem.',
    tech: ['React', 'TypeScript', 'Canvas API'],
    year: '2024'
  },
  {
    id: 's4t5u6',
    displayId: '005',
    title: 'Signal',
    description: 'High-density real-time analytics dashboard with predictive modeling and D3 visualization.',
    tech: ['D3.js', 'Next.js', 'Node.js'],
    year: '2023'
  }
];

const Projects: React.FC = () => {
  const { isTransitioning } = useStage();
  const [showAll, setShowAll] = useState(false);

  const displayedProjects = showAll ? PROJECTS_DATA : PROJECTS_DATA.slice(0, 3);

  return (
    <div className={`${styles.container} ${isTransitioning ? styles.exiting : ''}`}>
      <div className={styles.content}>
        <div className={styles.label}>
          <span className={styles.systemId}>id="x2b31z"</span>
          <span className={styles.accentDot}>•</span> PROJECTS
        </div>

        <div className={styles.grid}>
          {displayedProjects.map((project, idx) => (
            <div 
              key={project.id} 
              className={styles.card}
              style={{ animationDelay: `${idx * 120}ms` }}
              onClick={() => console.log(`Open ${project.title}`)}
            >
              <div className={styles.cardHeader}>
                <span className={styles.projectId}>id="{project.id}"</span>
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
              <span className={styles.systemId}>id="1xj5fx"</span>
              <span className={styles.plus}>+</span> EXPLORE MORE SYSTEMS
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Projects;
