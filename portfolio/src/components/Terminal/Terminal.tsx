import React, { useEffect, useRef, useState } from 'react';
import { findProject, NAV_STAGES, TERMINAL_COMMANDS, PROFILE } from '../../data/projects';
import { useStage } from '../../context/useStage';
import type { Stage } from '../../types';
import styles from './Terminal.module.css';

type TerminalLine = {
  id: number;
  kind: 'input' | 'output' | 'error';
  text: string;
};

const PROMPT = '~/portfolio >';

const normalizeScene = (scene: string): Stage | null => {
  const normalized = scene.toLowerCase().trim();

  if (normalized === 'about' || normalized === 'home') return 'intro';
  if (NAV_STAGES.includes(normalized as Stage)) return normalized as Stage;

  return null;
};

const Terminal: React.FC = () => {
  const {
    currentStage,
    setStage,
    openModal,
    isTerminalOpen,
    closeTerminal
  } = useStage();
  const [input, setInput] = useState('');
  const [isRendered, setIsRendered] = useState(false);
  const [lines, setLines] = useState<TerminalLine[]>([
    { id: 1, kind: 'output', text: "System control ready. Type 'help'." }
  ]);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const lineIdRef = useRef(2);

  const terminalAvailable = currentStage !== 'landing' && currentStage !== 'boot';

  const appendLine = (kind: TerminalLine['kind'], text: string) => {
    setLines((currentLines) => [
      ...currentLines,
      { id: lineIdRef.current++, kind, text }
    ]);
  };

  const navigateTo = (scene: Stage) => {
    setStage(scene);
    appendLine('output', `Opening ${scene[0].toUpperCase()}${scene.slice(1)} Scene...`);
  };

  const executeCommand = (rawCommand: string) => {
    const command = rawCommand.trim();
    appendLine('input', `${PROMPT} ${command || ''}`);

    if (!command) {
      appendLine('error', "Command not recognized. Type 'help'");
      return;
    }

    setCommandHistory((history) => [...history, command]);
    setHistoryIndex(null);

    const normalizedCommand = command.toLowerCase();
    const [base, ...args] = normalizedCommand.split(/\s+/);

    if (normalizedCommand === 'who am i') {
      appendLine('output', PROFILE.tagline);
      return;
    }

    switch (base) {
      case 'help':
        appendLine('output', TERMINAL_COMMANDS.join(' ') + ' goto <scene> open <project>');
        return;
      case 'about':
        appendLine('output', PROFILE.summary);
        return;
      case 'whoami':
        appendLine('output', PROFILE.tagline);
        return;
      case 'clear':
        setLines([]);
        return;
      case 'skills':
        navigateTo('skills');
        return;
      case 'projects':
        navigateTo('projects');
        return;
      case 'contact':
        navigateTo('contact');
        return;
    }

    if (base === 'goto' || base === 'nav') {
      const target = normalizeScene(args[0] ?? '');
      if (!target) {
        appendLine('error', "Scene not found. Try 'goto projects'");
        return;
      }

      navigateTo(target);
      return;
    }

    if (base === 'open') {
      const projectQuery = args.join(' ');
      const project = findProject(projectQuery);

      if (!project) {
        appendLine('error', "Project not found. Try 'open smart-search'");
        return;
      }

      appendLine('output', `Opening ${project.title}...`);
      setStage('projects');
      window.setTimeout(() => openModal(project), currentStage === 'projects' ? 80 : 520);
      return;
    }

    appendLine('error', `Unknown command '${base}'. Type 'help'`);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const command = input;
    setInput('');
    window.setTimeout(() => executeCommand(command), 35);
  };

  const handleInputKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      const nextIndex = historyIndex === null ? commandHistory.length - 1 : Math.max(historyIndex - 1, 0);
      if (commandHistory[nextIndex]) {
        setHistoryIndex(nextIndex);
        setInput(commandHistory[nextIndex]);
      }
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      if (historyIndex === null) return;

      const nextIndex = historyIndex + 1;
      if (nextIndex >= commandHistory.length) {
        setHistoryIndex(null);
        setInput('');
      } else {
        setHistoryIndex(nextIndex);
        setInput(commandHistory[nextIndex]);
      }
    }
  };

  useEffect(() => {
    if (isTerminalOpen) inputRef.current?.focus();
  }, [isTerminalOpen]);

  useEffect(() => {
    if (isTerminalOpen) {
      const timeout = window.setTimeout(() => setIsRendered(true), 0);
      return () => window.clearTimeout(timeout);
    }

    inputRef.current?.blur();
    const timeout = window.setTimeout(() => setIsRendered(false), 300);
    return () => window.clearTimeout(timeout);
  }, [isTerminalOpen]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [lines]);

  if (!terminalAvailable) return null;

  return (
    <>
      {isRendered && (
        <div className={`${styles.overlay} ${isTerminalOpen ? styles.open : ''}`}>
          <div className={styles.backdrop} onClick={closeTerminal} />
          <section className={styles.panel} role="dialog" aria-label="System terminal" aria-modal="true">
            <div className={styles.header}>
              <span className={styles.status}>SYS://TERMINAL</span>
              <button className={styles.closeBtn} onClick={closeTerminal} aria-label="Close terminal">x</button>
            </div>

            <div className={styles.output} ref={scrollRef}>
              {lines.map((line) => (
                <div key={line.id} className={`${styles.line} ${styles[line.kind]}`}>
                  {line.text}
                </div>
              ))}
            </div>

            <form className={styles.inputRow} onSubmit={handleSubmit}>
              <label className={styles.prompt} htmlFor="terminal-command">{PROMPT}</label>
              <input
                id="terminal-command"
                ref={inputRef}
                className={styles.input}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleInputKeyDown}
                autoComplete="off"
                spellCheck={false}
              />
              <span className={styles.cursor} />
            </form>
          </section>
        </div>
      )}
    </>
  );
};

export default Terminal;
