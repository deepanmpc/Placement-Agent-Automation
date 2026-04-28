import React, { useState } from 'react';
import { useStage } from '../../context/useStage';
import type { Project } from '../../types';
import styles from './Projects.module.css';

const PROJECTS_DATA: Project[] = [
  {
    id: 'bkw1f8',
    displayId: '001',
    title: 'SMART-SEARCH',
    description: 'Semantic file system search tool with zero-configuration natural language understanding.',
    problem: 'Traditional file search is limited to exact keywords, making it difficult to find files based on concepts or context.',
    solution: 'Engineered a RAG-based search tool using vector embeddings and LLMs to enable semantic retrieval without any pre-configuration.',
    impact: 'Significantly reduced time spent searching for internal documentation and unstructured project files.',
    tech: ['Python', 'RAG', 'Vector DB', 'LLMs'],
    year: '2024'
  },
  {
    id: 'nj2m9x',
    displayId: '002',
    title: 'LaRa',
    description: 'Low-cost AI therapy companion for specially-abled children with an offline 4-layer pipeline.',
    problem: 'Professional therapy tools are often prohibitively expensive and require constant high-speed internet access.',
    solution: 'Developed a modular AI companion with a custom 4-layer offline-capable pipeline, blending computer vision and natural language processing.',
    impact: 'Created an accessible, locally-operable therapeutic tool prototype for underserved communities.',
    tech: ['PyTorch', 'Robotics', 'CV', 'NLP'],
    year: '2023'
  },
  {
    id: 'x8y9z0',
    displayId: '003',
    title: 'ISL Recognition',
    description: 'Real-time Indian Sign Language recognition system achieving 99.8% accuracy for accessibility.',
    problem: 'Communication barriers between the hearing-impaired and the general public due to lack of real-time translation tools.',
    solution: 'Built a real-time ISL recognition system using CNNs and OpenCV, optimized for high FPS and accuracy in varying light conditions.',
    impact: 'Achieved 99.8% accuracy at 45 FPS, demonstrating the viability of real-time sign language translation on edge devices.',
    tech: ['TensorFlow', 'OpenCV', 'CNN', 'Python'],
    year: '2023'
  },
  {
    id: 'p1q2r3',
    displayId: '004',
    title: 'Flux OS',
    description: 'Browser-based operating system interface with a custom window manager and virtual filesystem.',
    problem: 'Web applications often lack the organizational power and multi-tasking capabilities of native desktop environments.',
    solution: 'Designed a fully functional web-based OS interface with a custom drag-and-drop window manager and a virtualized filesystem.',
    impact: 'Showcased a modular architecture for complex browser-based productivity tools.',
    tech: ['React', 'TypeScript', 'Canvas API', 'Framer Motion'],
    year: '2024'
  },
  {
    id: 's4t5u6',
    displayId: '005',
    title: 'Signal',
    description: 'High-density real-time analytics dashboard with predictive modeling and D3 visualization.',
    problem: 'Large-scale real-time data streams are often difficult to visualize and analyze effectively for immediate decision-making.',
    solution: 'Developed a high-density dashboard featuring real-time D3 visualizations and integrated predictive ML models.',
    impact: 'Provided a centralized platform for monitoring complex system metrics with real-time alerting capabilities.',
    tech: ['D3.js', 'Next.js', 'Node.js', 'MLOps'],
    year: '2023'
  }
];

const Projects: React.FC = () => {
  const { isTransitioning, openModal } = useStage();
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
              onClick={() => openModal(project)}
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
