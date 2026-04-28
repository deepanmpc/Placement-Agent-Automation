import React from 'react';
import styles from './Intro.module.css';

const Intro: React.FC = () => {
  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <div className={styles.availability}>
          <span className={styles.dim}>//</span> Currently available for work
          <span className={styles.typingCursor} />
        </div>
        
        <h1 className={`${styles.name} syne`}>
          Alex<br />
          Mercer.
        </h1>
        
        <div className={styles.role}>
          Frontend Engineer <span className={styles.dot}>·</span> UI Designer <span className={styles.dot}>·</span> Creative Coder
        </div>
        
        <p className={styles.tagline}>
          I build interfaces that feel alive — blending system thinking with craft.
        </p>

        <div className={styles.actions}>
          <button className={styles.btn}>Skills</button>
          <button className={styles.btn}>Projects</button>
          <button className={styles.btn}>Contact</button>
        </div>
      </div>
    </div>
  );
};

export default Intro;
