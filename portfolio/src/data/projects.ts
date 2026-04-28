import type { Project, Stage } from '../types';

export const PROJECTS_DATA: Project[] = [
  {
    id: 'bkw1f8',
    displayId: '001',
    title: 'SMART-SEARCH',
    description: 'Semantic file system search tool with zero-configuration natural language understanding.',
    problem: 'Traditional file search is limited to exact keywords, making it difficult to find files based on concepts or context.',
    solution: 'Engineered a RAG-based search tool using vector embeddings and LLMs to enable semantic retrieval without any pre-configuration.',
    impact: 'Significantly reduced time spent searching for internal documentation and unstructured project files.',
    tech: ['Python', 'RAG', 'Vector DB', 'LLMs'],
    year: '2024'
  },
  {
    id: 'nj2m9x',
    displayId: '002',
    title: 'LaRa',
    description: 'Low-cost AI therapy companion for specially-abled children with an offline 4-layer pipeline.',
    problem: 'Professional therapy tools are often prohibitively expensive and require constant high-speed internet access.',
    solution: 'Developed a modular AI companion with a custom 4-layer offline-capable pipeline, blending computer vision and natural language processing.',
    impact: 'Created an accessible, locally-operable therapeutic tool prototype for underserved communities.',
    tech: ['PyTorch', 'Robotics', 'CV', 'NLP'],
    year: '2023'
  },
  {
    id: 'x8y9z0',
    displayId: '003',
    title: 'ISL Recognition',
    description: 'Real-time Indian Sign Language recognition system achieving 99.8% accuracy for accessibility.',
    problem: 'Communication barriers between the hearing-impaired and the general public due to lack of real-time translation tools.',
    solution: 'Built a real-time ISL recognition system using CNNs and OpenCV, optimized for high FPS and accuracy in varying light conditions.',
    impact: 'Achieved 99.8% accuracy at 45 FPS, demonstrating the viability of real-time sign language translation on edge devices.',
    tech: ['TensorFlow', 'OpenCV', 'CNN', 'Python'],
    year: '2023'
  },
  {
    id: 'p1q2r3',
    displayId: '004',
    title: 'Flux OS',
    description: 'Browser-based operating system interface with a custom window manager and virtual filesystem.',
    problem: 'Web applications often lack the organizational power and multi-tasking capabilities of native desktop environments.',
    solution: 'Designed a fully functional web-based OS interface with a custom drag-and-drop window manager and a virtualized filesystem.',
    impact: 'Showcased a modular architecture for complex browser-based productivity tools.',
    tech: ['React', 'TypeScript', 'Canvas API', 'Framer Motion'],
    year: '2024'
  },
  {
    id: 's4t5u6',
    displayId: '005',
    title: 'Signal',
    description: 'High-density real-time analytics dashboard with predictive modeling and D3 visualization.',
    problem: 'Large-scale real-time data streams are often difficult to visualize and analyze effectively for immediate decision-making.',
    solution: 'Developed a high-density dashboard featuring real-time D3 visualizations and integrated predictive ML models.',
    impact: 'Provided a centralized platform for monitoring complex system metrics with real-time alerting capabilities.',
    tech: ['D3.js', 'Next.js', 'Node.js', 'MLOps'],
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
  years: string;
  year: string;
}

export interface Certification {
  id: string;
  name: string;
  provider: string;
  detail: string;
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
  tagline: 'AI Engineer · Full-Stack Developer · Researcher',
  roles: ['AI Engineer', 'Full-Stack Developer', 'Researcher'],
  summary: 'Building the interface between AI and humans. Low-cost therapy companions, semantic search, and systems that actually make sense.',
  location: {
    lat: 12.3401,
    lng: 77.2901,
    coords: '12.3401°N 77.2901°E'
  }
};

export const EDUCATION: EducationInfo = {
  degree: 'B.Tech Computer Science',
  school: 'Vellore Institute of Technology',
  years: '2022 — 2026',
  year: '3rd Year'
};

export const CERTIFICATIONS: Certification[] = [
  { id: 's9d2mz', name: 'Google ML Certificate', provider: 'Coursera', detail: 'Machine Learning Specialization' },
  { id: 'c8k3w1', name: 'AWS Cloud Practitioner', provider: 'Amazon', detail: 'Cloud Fundamentals' },
  { id: '9m2zlr', name: 'Deep Learning Specialization', provider: 'Andrew Ng', detail: 'Neural Networks & Deep Learning' }
];

export const SKILLS: Skill[] = [
  { id: '1', name: 'React / Next.js', detail: 'Fast UIs, full-stack apps, and performance tuning for real-world use.' },
  { id: '2', name: 'AI / ML Engineering', detail: 'RAG pipelines, offline AI that runs without WiFi, and 99.8% ISL accuracy.' },
  { id: '3', name: 'TypeScript / Node.js', detail: 'Type-safe backends that don\'t break at 2am.' },
  { id: '4', name: 'Robotic-AI / CV', detail: 'Real-time vision on edge devices. No cloud required.' },
  { id: '5', name: 'Systems Design', detail: 'Modular architectures that actually scale.' },
  { id: '6', name: 'Python / Data Science', detail: 'ML models and data pipelines that deliver insights.' }
];

export const ACHIEVEMENTS: Achievement[] = [
  { id: '9m2zlr', text: '3rd Place — Rampage v2.6 Hackathon' },
  { id: 'j7x2qp', text: '500+ Active Users for AI Therapy System' },
  { id: 'c8k3w1', text: 'Top 5% — Kaggle ML Competition' }
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