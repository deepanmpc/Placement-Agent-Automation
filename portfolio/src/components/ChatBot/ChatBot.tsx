import React, { useEffect, useRef, useState } from 'react';
import { useStage } from '../../context/useStage';
import type { Stage } from '../../types';
import styles from './ChatBot.module.css';

type Message = {
  id: number;
  role: 'bot' | 'user';
  text: string;
};

type QuickAction = {
  label: string;
  prompt: string;
};

const QUICK_ACTIONS: QuickAction[] = [
  { label: 'Specialties?', prompt: 'specialties' },
  { label: 'Best work?', prompt: 'best work' },
  { label: 'Available for hire?', prompt: 'available for hire' },
  { label: 'Contact', prompt: 'contact' }
];

const FIRST_MESSAGE = "You're inside my portfolio. What do you want to explore?";

const ChatBot: React.FC = () => {
  const { currentStage, setStage, isChatOpen, closeChat } = useStage();
  const [isRendered, setIsRendered] = useState(false);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, role: 'bot', text: FIRST_MESSAGE }
  ]);
  const messageIdRef = useRef(2);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const chatAvailable = currentStage !== 'landing' && currentStage !== 'boot';

  const appendMessage = (role: Message['role'], text: string) => {
    setMessages((currentMessages) => [
      ...currentMessages,
      { id: messageIdRef.current++, role, text }
    ]);
  };

  const navigateTo = (stage: Stage, text: string) => {
    setStage(stage);
    return text;
  };

  const getResponse = (rawInput: string): string => {
    const text = rawInput.toLowerCase().trim();

    if (text.includes('project') || text.includes('work') || text.includes('portfolio')) {
      return navigateTo('projects', 'Alright. Opening projects.');
    }

    if (text.includes('skill') || text.includes('stack') || text.includes('special')) {
      return navigateTo('skills', 'Most of my work is AI systems, real-time interfaces, and full-stack products.');
    }

    if (text.includes('contact') || text.includes('email') || text.includes('reach')) {
      return navigateTo('contact', 'Opening contact. That is the cleanest path.');
    }

    if (text.includes('hire') || text.includes('available') || text.includes('freelance')) {
      return navigateTo('contact', 'Yes. I am open to serious builds. Contact is the fastest route.');
    }

    if (text.includes('about') || text.includes('who')) {
      return 'I build AI systems and interfaces that feel alive. Less static portfolio, more operating layer.';
    }

    return 'Not sure what you mean. Ask about skills, projects, or availability.';
  };

  const sendMessage = (value: string) => {
    const trimmedValue = value.trim();
    if (!trimmedValue || isTyping) return;

    appendMessage('user', trimmedValue);
    setInput('');
    setIsTyping(true);

    window.setTimeout(() => {
      appendMessage('bot', getResponse(trimmedValue));
      setIsTyping(false);
    }, 420);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    sendMessage(input);
  };

  useEffect(() => {
    if (isChatOpen) {
      const timeout = window.setTimeout(() => {
        setIsRendered(true);
        inputRef.current?.focus();
      }, 0);
      return () => window.clearTimeout(timeout);
    }

    inputRef.current?.blur();
    const timeout = window.setTimeout(() => setIsRendered(false), 300);
    return () => window.clearTimeout(timeout);
  }, [isChatOpen]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, isTyping]);

  if (!chatAvailable) return null;

  return (
    <>
      {isRendered && (
        <div className={`${styles.overlay} ${isChatOpen ? styles.open : ''}`}>
          <div className={styles.backdrop} onClick={closeChat} />
          <section className={styles.panel} role="dialog" aria-label="System chat" aria-modal="true">
            <header className={styles.header}>
              <div>
                <span className={styles.status}>SYS://CHAT</span>
                <h2 className={styles.title}>System Assistant</h2>
              </div>
              <button className={styles.closeBtn} onClick={closeChat} aria-label="Close chat">x</button>
            </header>

            <div className={styles.messages} ref={scrollRef}>
              {messages.map((message) => (
                <div key={message.id} className={`${styles.message} ${styles[message.role]}`}>
                  {message.text}
                </div>
              ))}
              {isTyping && (
                <div className={`${styles.message} ${styles.bot} ${styles.typing}`} aria-label="Assistant typing">
                  <span />
                  <span />
                  <span />
                </div>
              )}
            </div>

            <div className={styles.quickActions}>
              {QUICK_ACTIONS.map((action) => (
                <button
                  key={action.label}
                  className={styles.quickBtn}
                  onClick={() => sendMessage(action.prompt)}
                >
                  {action.label}
                </button>
              ))}
            </div>

            <form className={styles.inputRow} onSubmit={handleSubmit}>
              <input
                ref={inputRef}
                className={styles.input}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask about skills, projects, contact..."
                autoComplete="off"
              />
              <button className={styles.sendBtn} type="submit">Send</button>
            </form>
          </section>
        </div>
      )}
    </>
  );
};

export default ChatBot;
