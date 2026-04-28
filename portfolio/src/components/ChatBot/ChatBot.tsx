import React, { useEffect, useRef, useState } from 'react';
import { useStage } from '../../context/useStage';
import styles from './ChatBot.module.css';

type Message = {
  id: number;
  role: 'bot' | 'user';
  text: string;
  action?: QuickAction;
};

type QuickAction = {
  label: string;
  text: string;
};

const QUICK_ACTIONS: QuickAction[] = [
  { label: 'Projects', text: 'projects' },
  { label: 'Available?', text: 'available' },
  { label: 'Contact', text: 'contact' }
];

const FIRST_MESSAGE: Message = {
  id: 0,
  role: 'bot',
  text: "SYSTEM ACTIVE. Query my build profile.",
  action: { label: 'View Projects', text: 'projects' }
};

const ChatBot: React.FC = () => {
  const { currentStage, isChatOpen, closeChat } = useStage();
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const messageIdRef = useRef(1);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const hasSentFirstMsg = useRef(false);

  const chatAvailable = currentStage !== 'landing' && currentStage !== 'boot';

  useEffect(() => {
    if (isChatOpen) {
      document.body.style.overflow = 'hidden';
      if (!hasSentFirstMsg.current) {
        hasSentFirstMsg.current = true;
        setIsTyping(true);
        const timer = setTimeout(() => {
          setMessages([FIRST_MESSAGE]);
          setIsTyping(false);
          inputRef.current?.focus();
        }, 500);
        return () => clearTimeout(timer);
      }
    } else {
      document.body.style.overflow = '';
      hasSentFirstMsg.current = false;
      setMessages([]);
    }
  }, [isChatOpen]);

  const appendMessage = (role: Message['role'], text: string) => {
    setMessages((currentMessages) => [
      ...currentMessages,
      { id: messageIdRef.current++, role, text }
    ]);
  };

  const sendMessage = async (value: string) => {
    const trimmedValue = value.trim();
    if (!trimmedValue || isTyping) return;

    appendMessage('user', trimmedValue);
    setInput('');
    setIsTyping(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmedValue }),
      });
      const data = await res.json();
      appendMessage('bot', data.reply || 'System unavailable.');
    } catch {
      appendMessage('bot', 'System error. Try again.');
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    sendMessage(input);
  };

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, isTyping]);

  if (!chatAvailable) return null;

  return (
    <>
      {isChatOpen && (
        <div className={`${styles.overlay} ${styles.open}`}>
          <div className={styles.backdrop} onClick={closeChat} />
          <section className={styles.panel} role="dialog" aria-label="System chat" aria-modal="true">
            <header className={styles.header}>
              <div>
                <span className={styles.status}>SYS::CHAT</span>
                <h2 className={styles.title}>System Assistant</h2>
              </div>
              <button className={styles.closeBtn} onClick={closeChat} aria-label="Close chat">x</button>
            </header>

            <div className={styles.messages} ref={scrollRef}>
              {messages.map((message) => (
                <div key={message.id} className={`${styles.message} ${styles[message.role]}`}>
                  <p>{message.text}</p>
                  {message.action && (
                    <button className={styles.actionBtn} onClick={() => sendMessage(message.action!.text)}>
                      {'> '}{message.action.label}
                    </button>
                  )}
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
                  onClick={() => sendMessage(action.text)}
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