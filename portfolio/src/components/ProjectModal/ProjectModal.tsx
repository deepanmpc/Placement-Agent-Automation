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
          ← Back
        </button>
        
        <button className={styles.closeBtn} onClick={closeModal}>
          [ ESC ]
        </button>

        <header className={styles.header}>
          <div className={styles.headerTop}>
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
          {modalProject.repo && (
            <button className={styles.primaryBtn} onClick={() => window.open(modalProject.repo, '_blank')}>
              [ View Code ]
            </button>
          )}
          {modalProject.link && (
            <button className={styles.secondaryBtn} onClick={() => window.open(modalProject.link, '_blank')}>
              [ Try Project ]
            </button>
          )}
          <button className={styles.secondaryBtn} onClick={closeModal}>
            [ Close ]
          </button>
        </footer>
      </div>
    </div>
  );
};

export default ProjectModal;
