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
  { label: 'Skills', text: 'skills' },
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

const SKILL_DETAILS: Record<string, string> = {
  react: "ResumeAnalyse, 3D configurator. Component architecture, state flow, performance.",
  typescript: "All frontend systems. Type safety, reduced bugs, maintainability.",
  fastapi: "RAG pipelines, real-time AI APIs. Async design, low-latency endpoints.",
  pytorch: "SignSpeak AI, vision systems. Model optimization, real-time inference.",
  computervision: "Sign language detection, gesture systems. Frame processing, latency trade-offs.",
  rag: "ResumeAnalyse, LaRa memory. LLM + vector search for context.",
  faiss: "50K+ file search. Indexing strategies, retrieval speed.",
  vectordb: "ChromaDB for semantic search. Efficient structuring for accuracy.",
  docker: "AI services, microservices. Environment consistency, orchestration.",
  microservices: "LaRa AI platform. Decoupling, communication patterns, scalability.",
  threejs: "3D apparel visualization. Rendering pipelines, WebGL performance.",
  nodejs: "Backend utilities, API handling. Event-driven architecture.",
  semanticsearch: "Multi-modal search over large datasets. Embedding retrieval, relevance ranking.",
  webrtc: "Real-time voice processing. Stream handling, low-latency constraints.",
  llm: "RAG pipelines, chatbots. Prompt control, response shaping, integration.",
  langchain: "RAG systems, agent design. Chain composition, memory management.",
  aws: "Cloud deployment, serverless. Scalability, managed services.",
};

const getResponse = (rawInput: string): string => {
  const text = rawInput.toLowerCase().trim();

  if (text.includes('project') || text.includes('work')) {
    return "LaRa combines speech, memory, and real-time AI. SignSpeak hits 45 FPS. Check projects.";
  }

  if (text === 'skills') {
    return "React, TypeScript, Python, PyTorch, RAG, FastAPI, FAISS, Docker, CV, LangChain, Vector DBs, AWS.";
  }

  const matchedSkill = Object.keys(SKILL_DETAILS).find(skill => text.includes(skill));
  if (matchedSkill) {
    return SKILL_DETAILS[matchedSkill];
  }

  if (text.includes('contact') || text.includes('email') || text.includes('reach')) {
    return "2300032731cse3@gmail.com | linkedin.com/in/deepanmpc/";
  }

  if (text.includes('hire') || text.includes('available')) {
    return "Yes. Got a problem worth solving? Let's talk.";
  }

  if (text.includes('who') || text.includes('about')) {
    return "AI Systems Engineer. RAG pipelines, semantic search, edge inference.";
  }

  if (text.includes('best')) {
    return "LaRa. RAG + speech + microservices. Real-time, memory-backed, scalable.";
  }

  return "Ask about skills, projects, or availability.";
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