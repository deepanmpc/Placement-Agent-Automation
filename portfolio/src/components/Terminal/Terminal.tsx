import React, { useEffect, useRef, useState } from 'react';
import { findProject, NAV_STAGES, PROFILE } from '../../data/projects';
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
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const terminalAvailable = currentStage !== 'landing' && currentStage !== 'boot';

  const startupLines: TerminalLine[] = [
    { id: 1, kind: 'output', text: 'Terminal v1.0.0 initialized.' },
    { id: 2, kind: 'output', text: "Type 'help' for available commands." },
    { id: 3, kind: 'output', text: "Try 'goto skills', 'goto projects', or 'goto contact' to navigate." }
  ];

  const [lines, setLines] = useState<TerminalLine[]>(startupLines);
  const lineIdRef = useRef(5);

  const appendLine = (kind: TerminalLine['kind'], text: string) => {
    setLines((prev) => [
      ...prev,
      { id: lineIdRef.current++, kind, text }
    ]);
  };

  const navigateTo = (scene: Stage) => {
    setStage(scene);
    appendLine('output', `Opening ${scene[0].toUpperCase()}${scene.slice(1)} Scene...`);
    setTimeout(() => {
      appendLine('output', `${scene[0].toUpperCase()}${scene.slice(1)} Scene Opened.`);
    }, 600);
  };

  const executeCommand = (rawCommand: string) => {
    const command = rawCommand.trim();
    appendLine('input', `${PROMPT} ${command || ''}`);

    if (!command) {
      appendLine('error', "Command not recognized. Type 'help'");
      return;
    }

    setCommandHistory((prev) => [...prev, command]);
    setHistoryIndex(null);

    const normalizedCommand = command.toLowerCase();
    const [base, ...args] = normalizedCommand.split(/\s+/);

    if (normalizedCommand === 'who am i') {
      appendLine('output', PROFILE.tagline);
      return;
    }

switch (base) {
      case 'help':
        appendLine('output', '=== AVAILABLE COMMANDS ===');
        appendLine('output', '  about      - Display profile summary');
        appendLine('output', '  whoami     - Display who you are');
        appendLine('output', '  clear      - Clear terminal');
        appendLine('output', '');
        appendLine('output', '=== NAVIGATION ===');
        appendLine('output', '  goto intro    - Go to Intro section');
        appendLine('output', '  goto skills  - Go to Skills section');
        appendLine('output', '  goto projects - Go to Projects section');
        appendLine('output', '  goto contact - Go to Contact section');
        appendLine('output', '  Example: goto projects');
        appendLine('output', '');
        appendLine('output', '=== LINKS ===');
        appendLine('output', '  github     - Open GitHub profile');
        appendLine('output', '  linkedin   - Open LinkedIn profile');
        appendLine('output', '');
        appendLine('output', '=== PROJECT ===');
        appendLine('output', '  open <name> - Open project detail');
        appendLine('output', '  Examples: open lara, open signspeak');
        appendLine('output', '');
        appendLine('output', 'Type command and press Enter.');
        return;
      case 'whoami':
        appendLine('output', PROFILE.tagline);
        return;
      case 'clear':
        setLines(startupLines);
        appendLine('output', 'Terminal cleared.');
        return;
      case 'github':
        window.open('https://github.com/deepanmpc', '_blank');
        appendLine('output', 'Opening GitHub profile in new tab...');
        appendLine('output', 'GitHub opened.');
        return;
      case 'linkedin':
        window.open('https://www.linkedin.com/in/deepanmpc/', '_blank');
        appendLine('output', 'Opening LinkedIn profile in new tab...');
        appendLine('output', 'LinkedIn opened.');
        return;
      case 'skills':
        appendLine('error', "Use 'goto skills' to navigate to Skills.");
        appendLine('output', 'Example: goto skills');
        return;
      case 'projects':
        appendLine('error', "Use 'goto projects' to navigate to Projects.");
        appendLine('output', 'Example: goto projects');
        return;
      case 'contact':
        appendLine('error', "Use 'goto contact' to navigate to Contact.");
        appendLine('output', 'Example: goto contact');
        return;
      case 'intro':
        appendLine('error', "Use 'goto intro' to navigate to Intro.");
        appendLine('output', 'Example: goto intro');
        return;
    }

    if (base === 'goto' || base === 'nav') {
      const target = normalizeScene(args[0] ?? '');
      if (!target) {
        appendLine('error', "Scene not found. Try 'goto projects'");
        return;
      }

      appendLine('output', `Navigating to ${target[0].toUpperCase()}${target.slice(1)}...`);
      navigateTo(target);
      return;
    }

    if (base === 'open') {
      const projectQuery = args.join(' ');
      const project = findProject(projectQuery);

      if (!project) {
        appendLine('error', 'Project not found. Try "open lara"');
        return;
      }

      appendLine('output', `Loading ${project.title}...`);
      setStage('projects');
      window.setTimeout(() => {
        openModal(project);
        appendLine('output', `${project.title} opened.`);
      }, currentStage === 'projects' ? 80 : 520);
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
              <span className={styles.status}>SYS::TERMINAL</span>
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