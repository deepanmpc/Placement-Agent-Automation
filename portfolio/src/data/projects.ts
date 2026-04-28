import type { Project, Stage } from '../types';

export const PROJECTS_DATA: Project[] = [
  {
    id: 'lar1a',
    displayId: '001',
    title: 'LaRa',
    description: 'Real-time AI platform combining speech pipelines, RAG memory, and deterministic decision systems.',
    problem: 'Users need personalized AI that remembers context across sessions without privacy concerns.',
    solution: 'Built a modular AI system with speech pipelines, vector-based memory, and FSM-driven responses.',
    impact: 'Deployed for neurodiverse users with offline capabilities.',
    tech: ['FastAPI', 'Docker', 'Faster-Whisper', 'RAG', 'Microservices'],
    year: '2024'
  },
  {
    id: 'sis2gn',
    displayId: '002',
    title: 'SignSpeak AI',
    description: 'Real-time sign language recognition system with edge inference at 45 FPS.',
    problem: 'Communication barriers between hearing-impaired and general public.',
    solution: 'Optimized CNN models for edge devices achieving real-time inference.',
    impact: '45 FPS on edge devices, helping real-time communication.',
    tech: ['PyTorch', 'CNN', 'OpenCV', 'NVIDIA GPUs'],
    year: '2024'
  },
  {
    id: 'res3ume',
    displayId: '003',
    title: 'ResumeAnalyse',
    description: 'RAG-based semantic matching system reducing recruiter effort by 50%.',
    problem: 'Recruiters spend excessive time screening resumes manually.',
    solution: 'Semantic matching with sentence embeddings and vector search.',
    impact: '50% reduction in recruiter screening time.',
    tech: ['Sentence Transformers', 'ChromaDB', 'Mistral', 'React'],
    year: '2024'
  },
  {
    id: 'sea4rch',
    displayId: '004',
    title: 'Search Wizard',
    description: 'Multi-modal semantic search engine over 50K+ files with sub-400ms retrieval.',
    problem: 'Finding files across large repositories takes too long.',
    solution: 'FAISS-indexed embeddings with Gemini for multi-modal queries.',
    impact: 'Sub-400ms retrieval across 50K+ files.',
    tech: ['FAISS', 'Gemini Embeddings', 'Electron', 'FastAPI'],
    year: '2024'
  },
  {
    id: 'aio5era',
    displayId: '005',
    title: 'AI Therapy System',
    description: 'AI system for neurodiverse users with offline speech processing.',
    problem: 'Professional therapy tools costly and require constant internet.',
    solution: 'WebRTC VAD with offline LLM and contextual memory.',
    impact: 'Offline-capable system for underserved communities.',
    tech: ['WebRTC VAD', 'LLM Integration', 'FSM Engine'],
    year: '2023'
  },
  {
    id: 'app6arel',
    displayId: '006',
    title: '3D Apparel Customizer',
    description: 'Full-stack platform with real-time 3D product preview.',
    problem: 'Customers cannot visualize custom apparel before purchase.',
    solution: 'Three.js-based real-time 3D preview integrated with backend.',
    impact: '8–10% increase in sales conversion.',
    tech: ['React', 'Three.js', 'Spring Boot'],
    year: '2023'
  }
];

export const findProject = (query: string): Project | undefined => {
  const normalized = query.trim().toLowerCase().replace(/[\s_-]+/g, '');

  return PROJECTS_DATA.find((project) => {
    const aliases = [
      project.id,
      project.displayId,
      project.title,
      project.title.replace(/[^a-z0-9]/gi, ''),
      project.title.split(/\s+/)[0]
    ];

    return aliases.some((alias) => alias.toLowerCase().replace(/[\s_-]+/g, '') === normalized);
  });
};

export interface ProfileInfo {
  name: string;
  tagline: string;
  roles: string[];
  summary: string;
  location: {
    lat: number;
    lng: number;
    coords: string;
  };
}

export interface EducationInfo {
  degree: string;
  school: string;
  cgpa: string;
  year: string;
  years: string;
}

export interface Certification {
  id: string;
  name: string;
  provider: string;
  year: string;
}

export interface Skill {
  id: string;
  name: string;
  detail: string;
}

export interface Achievement {
  id: string;
  text: string;
}

export interface ContactInfo {
  email: string;
  github: string;
  linkedin: string;
}

export const PROFILE: ProfileInfo = {
  name: 'Deepan Chandrasekaran',
  tagline: 'AI Engineer · Full-Stack Developer · Systems Architect',
  roles: ['AI Engineer', 'Full-Stack Developer', 'Systems Architect'],
  summary: 'Building the interface between AI and humans. Real-time systems, semantic search, and architectures that scale.',
  location: {
    lat: 12.3401,
    lng: 77.2901,
    coords: '12.3401°N 77.2901°E'
  }
};

export const EDUCATION: EducationInfo = {
  degree: 'B.Tech Computer Science & Engineering',
  school: 'KL University, Vijayawada',
  cgpa: '9.15',
  year: '2027',
  years: '2023 — 2027'
};

export const CERTIFICATIONS: Certification[] = [
  { id: 'nv1', name: 'NVIDIA DLI Deep Learning Fundamentals', provider: 'NVIDIA DLI', year: '2024' },
  { id: 'orc2', name: 'Generative AI Professional', provider: 'Oracle', year: '2025' },
  { id: 'orc3', name: 'AI Vector Search Professional', provider: 'Oracle', year: '2025' }
];

export const SKILLS: Skill[] = [
  { id: '1', name: 'React / Next.js', detail: 'Fast UIs, full-stack apps, and performance tuning for real-world use.' },
  { id: '2', name: 'AI / ML Engineering', detail: 'RAG pipelines, offline AI that runs without WiFi, and real-time CV systems.' },
  { id: '3', name: 'TypeScript / Node.js', detail: 'Type-safe backends that don\'t break at 2am.' },
  { id: '4', name: 'Computer Vision', detail: 'Real-time vision on edge devices. No cloud required.' },
  { id: '5', name: 'Systems Design', detail: 'Modular architectures that actually scale.' },
  { id: '6', name: 'Python / Data Science', detail: 'ML models and data pipelines that deliver insights.' }
];

export const ACHIEVEMENTS: Achievement[] = [
  { id: 'ach1', text: '3rd Place — RAMPAGE V26 National Hackathon' },
  { id: 'ach2', text: 'Built real-time AI systems with 45 FPS inference' },
  { id: 'ach3', text: 'Developed RAG pipelines with 90%+ retrieval accuracy' },
  { id: 'ach4', text: 'Engineered systems used for real-world applications' }
];

export const CONTACT: ContactInfo = {
  email: 'deepan@example.com',
  github: 'https://github.com/deepan',
  linkedin: 'https://linkedin.com/in/deepan'
};

export const TERMINAL_COMMANDS = [
  'help', 'about', 'skills', 'projects', 'contact', 'clear', 'goto', 'nav', 'open', 'whoami'
] as const;

export const NAV_STAGES: Stage[] = ['intro', 'skills', 'projects', 'contact'];