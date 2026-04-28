import React, { useEffect, useCallback } from 'react';
import { useStage } from '../../context/useStage';
import styles from './ProjectModal.module.css';

const ProjectModal: React.FC = () => {
  const { modalProject, closeModal } = useStage();

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      closeModal();
    }
  }, [closeModal]);

  useEffect(() => {
    if (modalProject) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [modalProject, handleKeyDown]);

  if (!modalProject) return null;

  return (
    <div className={styles.overlay} onClick={closeModal}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.backBtn} onClick={closeModal}>
          <span className={styles.dimId}>id="h5t3lo"</span> ← Back
        </button>
        
        <button className={styles.closeBtn} onClick={closeModal}>
          <span className={styles.dimId}>id="3gk9ht"</span> [ ESC ]
        </button>

        <header className={styles.header}>
          <div className={styles.headerTop}>
            <span className={styles.dimId}>id="z6g9p2"</span>
            <h2 className={`${styles.title} syne`}>{modalProject.title}</h2>
          </div>
          <div className={styles.meta}>
            {modalProject.tech.join(' · ')} · {modalProject.year}
          </div>
        </header>

        <div className={styles.content}>
          <section className={styles.section}>
            <h4 className={styles.sectionLabel}>PROBLEM</h4>
            <p className={styles.text}>{modalProject.problem || modalProject.description}</p>
          </section>

          <section className={styles.section}>
            <h4 className={styles.sectionLabel}>SOLUTION</h4>
            <p className={styles.text}>{modalProject.solution || "Implementation detail pending."}</p>
          </section>

          <section className={styles.section}>
            <h4 className={styles.sectionLabel}>IMPACT</h4>
            <p className={styles.text}>{modalProject.impact || "Project result details pending."}</p>
          </section>

          <section className={styles.section}>
            <h4 className={styles.sectionLabel}>TECH STACK</h4>
            <div className={styles.techList}>
              {modalProject.tech.map(t => (
                <span key={t} className={styles.techItem}>{t}</span>
              ))}
            </div>
          </section>
        </div>

        <footer className={styles.actions}>
          <button className={styles.primaryBtn} onClick={() => modalProject.link && window.open(modalProject.link, '_blank')}>
            <span className={styles.dimId}>id="c7x5bd"</span> [ View Project ]
          </button>
          <button className={styles.secondaryBtn} onClick={closeModal}>
            [ Close ]
          </button>
        </footer>
      </div>
    </div>
  );
};

export default ProjectModal;
