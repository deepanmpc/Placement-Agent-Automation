import React from 'react';
import { useStage } from '../../context/useStage';
import styles from './Contact.module.css';

const Contact: React.FC = () => {
  const { isTransitioning } = useStage();

  return (
    <div className={`${styles.container} ${isTransitioning ? styles.exiting : ''}`}>
      <div className={styles.content}>
        <div className={styles.label}>
          <span className={styles.accentDot}>•</span> CONTACT
        </div>

        <h2 className={`${styles.title} syne`}>Open channel.</h2>
        <p className={styles.copy}>
          I am available for AI systems, full-stack products, and research-heavy builds.
        </p>

        <div className={styles.links}>
          <a className={styles.link} href="mailto:2300032731cse3@gmail.com">
            <span className={styles.linkLabel}>EMAIL</span>
            <span>2300032731cse3@gmail.com</span>
          </a>
          <a className={styles.link} href="https://github.com/deepanmpc" target="_blank" rel="noreferrer">
            <span className={styles.linkLabel}>GITHUB</span>
            <span>github.com/deepanmpc</span>
          </a>
          <a className={styles.link} href="https://www.linkedin.com/in/deepanmpc/" target="_blank" rel="noreferrer">
            <span className={styles.linkLabel}>LINKEDIN</span>
            <span>linkedin.com/in/deepanmpc</span>
          </a>
        </div>
      </div>
    </div>
  );
};

export default Contact;
