import type {
  Student, CandidateRanking, JDRequirements, PipelineStage,
} from '../types';

export const PIPELINE_STAGES: PipelineStage[] = [
  {
    id: 'jd-parse',
    name: 'JD Parsing',
    description: 'Extract hiring requirements from job description',
    status: 'completed',
  },
  {
    id: 'hard-filter',
    name: 'Hard Filtering',
    description: 'Remove ineligible students (CGPA, branch, backlogs)',
    status: 'completed',
  },
  {
    id: 'rule-rank',
    name: 'Weighted Rule Ranking',
    description: 'Score candidates on structured data (skills, coding, GitHub)',
    status: 'active',
  },
  {
    id: 'semantic-rank',
    name: 'Semantic Ranking',
    description: 'Measure semantic relevance between resume and JD via embeddings',
    status: 'pending',
  },
  {
    id: 'ml-rank',
    name: 'ML Ranking',
    description: 'Predict placement probability using historical data',
    status: 'future',
  },
  {
    id: 'aggregate',
    name: 'Score Aggregation',
    description: 'Combine all scores into final weighted score',
    status: 'pending',
  },
  {
    id: 'explain',
    name: 'Explainability',
    description: 'Generate human-readable ranking justification',
    status: 'pending',
  },
];

export const MOCK_JD: JDRequirements = {
  title: 'Software Development Engineer',
  company: 'TechCorp India',
  description:
    'We are looking for a skilled SDE with strong fundamentals in data structures, algorithms, and web development. The ideal candidate has experience with modern frameworks and a proven track record on coding platforms.',
  minCGPA: 7.0,
  allowedBranches: ['CSE', 'IT', 'ECE', 'EEE'],
  maxBacklogs: 0,
  graduationYear: 2026,
  mandatorySkills: ['Python', 'JavaScript', 'Data Structures', 'Algorithms', 'SQL'],
  preferredSkills: ['React', 'Node.js', 'Docker', 'AWS', 'TypeScript', 'Go'],
  minCodingScore: 50,
};

const BASE_STUDENTS: Student[] = [
  {
    id: 'STU001',
    personalInfo: {
      name: 'Arun Sharma',
      email: 'arun.sharma@college.edu',
      phone: '+91-9876543210',
      linkedin: 'linkedin.com/in/arunsharma',
      github: 'github.com/arunsharma',
      location: 'Mumbai, India',
    },
    education: {
      institution: 'Indian Institute of Technology',
      degree: 'B.Tech',
      specialization: 'Computer Science',
      cgpa: 8.9,
      startYear: 2022,
      endYear: 2026,
    },
    skills: ['Python', 'JavaScript'],
    projects: [
      {
        title: 'E-Commerce Platform',
        description: 'Full-stack e-commerce platform with payment gateway integration',
        technologies: ['React', 'Node.js', 'PostgreSQL', 'Redis', 'Docker'],
        url: 'github.com/arunsharma/ecommerce',
      },
      {
        title: 'Real-time Chat Application',
        description: 'WebSocket-based chat app with end-to-end encryption',
        technologies: ['React', 'Socket.io', 'MongoDB', 'Docker'],
        url: 'github.com/arunsharma/chat-app',
      },
      {
        title: 'ML Model Deployment Pipeline',
        description: 'Automated ML model deployment with CI/CD',
        technologies: ['Python', 'Docker', 'Kubernetes', 'AWS', 'MLflow'],
        url: 'github.com/arunsharma/ml-pipeline',
      },
    ],
    experience: [
      {
        company: 'Google Summer of Code',
        role: 'Contributor',
        duration: '3 months',
        description: 'Contributed to open-source Kubernetes project',
      },
    ],
    certifications: [
      { name: 'AWS Solutions Architect Associate', issuer: 'Amazon', year: 2025 },
      { name: 'Google Cloud Associate Engineer', issuer: 'Google', year: 2024 },
    ],
    achievements: [
      { title: 'CodeChef Rating 2100', description: 'Achieved 4-star rating on CodeChef' },
      { title: 'LeetCode Contest Top 10%', description: 'Ranked in top 10% in Weekly Contest 350' },
    ],
    github: {
      repositories: 48,
      stars: 320,
      forks: 145,
      languages: ['Python', 'JavaScript', 'TypeScript', 'Go', 'Rust'],
      commitCount: 1840,
      contributionConsistency: 92,
      openSourceActivity: ['Kubernetes', 'React', 'Node.js'],
      score: 88,
    },
    coding: {
      leetcode: { easySolved: 120, mediumSolved: 210, hardSolved: 65, contestRating: 1820, contestHistory: 28, score: 90 },
      codeforces: { rating: 1650, contestParticipation: 35, problemsSolved: 420, score: 78 },
      codechef: { rating: 2100, contestParticipation: 42, problemsSolved: 380, score: 85 },
      codingStrength: 86,
    },
    aptitudeScore: 92,
    communicationScore: 85,
  },
  {
    id: 'STU002',
    personalInfo: {
      name: 'Priya Patel',
      email: 'priya.patel@college.edu',
      phone: '+91-9876543211',
      linkedin: 'linkedin.com/in/priyapatel',
      github: 'github.com/priyapatel',
      location: 'Bangalore, India',
    },
    education: {
      institution: 'National Institute of Technology',
      degree: 'B.Tech',
      specialization: 'Computer Science',
      cgpa: 8.5,
      startYear: 2022,
      endYear: 2026,
    },
    skills: ['Python', 'JavaScript'],
    projects: [
      {
        title: 'Inventory Management System',
        description: 'Microservices-based inventory system for retail chain',
        technologies: ['Java', 'Spring Boot', 'PostgreSQL', 'Docker', 'React'],
        url: 'github.com/priyapatel/inventory',
      },
      {
        title: 'Weather Forecast Dashboard',
        description: 'Real-time weather visualization with predictive analytics',
        technologies: ['Python', 'Flask', 'React', 'PostgreSQL'],
        url: 'github.com/priyapatel/weather-dash',
      },
    ],
    experience: [],
    certifications: [
      { name: 'Oracle Java Certified', issuer: 'Oracle', year: 2025 },
    ],
    achievements: [
      { title: 'Hackathon Winner', description: 'Won Smart India Hackathon 2025' },
    ],
    github: {
      repositories: 32,
      stars: 180,
      forks: 78,
      languages: ['Python', 'JavaScript', 'Java'],
      commitCount: 980,
      contributionConsistency: 78,
      openSourceActivity: ['Spring Boot'],
      score: 72,
    },
    coding: {
      leetcode: { easySolved: 95, mediumSolved: 140, hardSolved: 30, contestRating: 1520, contestHistory: 18, score: 72 },
      codeforces: { rating: 1380, contestParticipation: 22, problemsSolved: 280, score: 65 },
      codechef: { rating: 1750, contestParticipation: 30, problemsSolved: 290, score: 72 },
      codingStrength: 70,
    },
    aptitudeScore: 85,
    communicationScore: 80,
  },
  {
    id: 'STU003',
    personalInfo: {
      name: 'Rohit Verma',
      email: 'rohit.verma@college.edu',
      phone: '+91-9876543212',
      linkedin: 'linkedin.com/in/rohitverma',
      github: 'github.com/rohitverma',
      location: 'Delhi, India',
    },
    education: {
      institution: 'Delhi Technological University',
      degree: 'B.Tech',
      specialization: 'Information Technology',
      cgpa: 9.2,
      startYear: 2022,
      endYear: 2026,
    },
    skills: ['Python', 'JavaScript'],
    projects: [
      {
        title: 'Code Review Bot',
        description: 'AI-powered code review assistant using LLMs',
        technologies: ['Python', 'FastAPI', 'OpenAI', 'React', 'Docker'],
        url: 'github.com/rohitverma/code-review-bot',
      },
      {
        title: 'Distributed Task Queue',
        description: 'Redis-based distributed task queue with monitoring',
        technologies: ['Rust', 'Redis', 'Docker', 'TypeScript'],
        url: 'github.com/rohitverma/task-queue',
      },
      {
        title: 'Personal Portfolio',
        description: 'Modern portfolio with 3D visualizations',
        technologies: ['Next.js', 'Three.js', 'TypeScript', 'Vercel'],
        url: 'github.com/rohitverma/portfolio',
      },
      {
        title: 'Web Analytics Dashboard',
        description: 'Real-time analytics with user behavior tracking',
        technologies: ['Python', 'React', 'PostgreSQL', 'D3.js'],
        url: 'github.com/rohitverma/analytics',
      },
    ],
    experience: [
      {
        company: 'Microsoft Internship',
        role: 'Software Engineer Intern',
        duration: '6 months',
        description: 'Worked on Azure DevOps pipeline optimization',
      },
      {
        company: 'Open Source Contributor',
        role: 'Contributor',
        duration: 'ongoing',
        description: 'Active contributor to Rust compiler and ecosystem',
      },
    ],
    certifications: [
      { name: 'AWS Certified Developer', issuer: 'Amazon', year: 2025 },
      { name: 'Rust Programming Certificate', issuer: 'Rust Foundation', year: 2024 },
    ],
    achievements: [
      { title: 'Codeforces Specialist', description: 'Achieved Specialist rating of 1750' },
      { title: 'Google Code Jam Round 2', description: 'Qualified for Round 2' },
      { title: 'Published Paper', description: 'Paper on distributed systems at IEEE conference' },
    ],
    github: {
      repositories: 56,
      stars: 890,
      forks: 310,
      languages: ['Python', 'TypeScript', 'Rust', 'JavaScript', 'Go'],
      commitCount: 3200,
      contributionConsistency: 96,
      openSourceActivity: ['Rust', 'Next.js', 'FastAPI'],
      score: 95,
    },
    coding: {
      leetcode: { easySolved: 150, mediumSolved: 280, hardSolved: 90, contestRating: 2100, contestHistory: 45, score: 95 },
      codeforces: { rating: 1750, contestParticipation: 48, problemsSolved: 560, score: 85 },
      codechef: { rating: 2200, contestParticipation: 55, problemsSolved: 450, score: 90 },
      codingStrength: 92,
    },
    aptitudeScore: 95,
    communicationScore: 78,
  },
  {
    id: 'STU004',
    personalInfo: {
      name: 'Sneha Gupta',
      email: 'sneha.gupta@college.edu',
      phone: '+91-9876543213',
      linkedin: 'linkedin.com/in/snehagupta',
      github: 'github.com/snehagupta',
      location: 'Pune, India',
    },
    education: {
      institution: 'College of Engineering Pune',
      degree: 'B.Tech',
      specialization: 'Electronics & Communication',
      cgpa: 7.8,
      startYear: 2022,
      endYear: 2026,
    },
    skills: ['Python', 'JavaScript'],
    projects: [
      {
        title: 'IoT Weather Station',
        description: 'ESP32-based weather monitoring system',
        technologies: ['Python', 'C', 'Arduino', 'Flask', 'MySQL'],
        url: 'github.com/snehagupta/iot-weather',
      },
    ],
    experience: [],
    certifications: [
      { name: 'Cisco CCNA', issuer: 'Cisco', year: 2024 },
    ],
    achievements: [
      { title: 'Robotics Competition', description: 'Won inter-college robotics competition' },
    ],
    github: {
      repositories: 18,
      stars: 45,
      forks: 22,
      languages: ['Python', 'C', 'MATLAB'],
      commitCount: 450,
      contributionConsistency: 55,
      openSourceActivity: [],
      score: 40,
    },
    coding: {
      leetcode: { easySolved: 60, mediumSolved: 40, hardSolved: 5, contestRating: 1100, contestHistory: 6, score: 35 },
      codeforces: { rating: 950, contestParticipation: 10, problemsSolved: 80, score: 30 },
      codechef: { rating: 1200, contestParticipation: 15, problemsSolved: 100, score: 38 },
      codingStrength: 34,
    },
    aptitudeScore: 72,
    communicationScore: 88,
  },
  {
    id: 'STU005',
    personalInfo: {
      name: 'Vikram Singh',
      email: 'vikram.singh@college.edu',
      phone: '+91-9876543214',
      linkedin: 'linkedin.com/in/vikramsingh',
      github: 'github.com/vikramsingh',
      location: 'Hyderabad, India',
    },
    education: {
      institution: 'Indian Institute of Technology',
      degree: 'B.Tech',
      specialization: 'Computer Science',
      cgpa: 6.5,
      startYear: 2022,
      endYear: 2026,
    },
    skills: ['Python', 'JavaScript'],
    projects: [
      {
        title: 'Todo App',
        description: 'Simple todo application with local storage',
        technologies: ['React', 'CSS', 'LocalStorage'],
        url: 'github.com/vikramsingh/todo',
      },
    ],
    experience: [],
    certifications: [],
    achievements: [],
    github: {
      repositories: 8,
      stars: 12,
      forks: 5,
      languages: ['JavaScript', 'HTML', 'CSS'],
      commitCount: 180,
      contributionConsistency: 30,
      openSourceActivity: [],
      score: 22,
    },
    coding: {
      leetcode: { easySolved: 30, mediumSolved: 10, hardSolved: 0, contestRating: 800, contestHistory: 2, score: 15 },
      codeforces: { rating: 700, contestParticipation: 5, problemsSolved: 30, score: 12 },
      codechef: { rating: 900, contestParticipation: 8, problemsSolved: 40, score: 18 },
      codingStrength: 16,
    },
    aptitudeScore: 65,
    communicationScore: 70,
  },
];

function computeFinalScore(student: Student): CandidateRanking {
  const w1 = 0.6;
  const w2 = 0.4;
  const w3 = 0.0;

  const skillMatch = student.skills.filter(
    (s) => MOCK_JD.mandatorySkills.includes(s),
  );
  const missingMandatory = MOCK_JD.mandatorySkills.filter(
    (s) => !student.skills.includes(s)
  );

  const academicScore = Math.min(100, (student.education.cgpa / 10) * 100);
  const skillMatchScore = Math.min(100, (skillMatch.length / MOCK_JD.mandatorySkills.length) * 100);
  const aptScore = student.aptitudeScore;
  const commScore = student.communicationScore;

  const ruleScoreBreakdown: Record<string, number> = {
    'Skill Match': Math.round(skillMatchScore * 0.3),
    'Coding Strength': Math.round(student.coding.codingStrength * 0.25),
    'GitHub Strength': Math.round(student.github.score * 0.15),
    'Academic Score': Math.round(academicScore * 0.15),
    'Aptitude Score': Math.round(aptScore * 0.08),
    'Communication Score': Math.round(commScore * 0.07),
  };
  const ruleScore = Object.values(ruleScoreBreakdown).reduce((a, b) => a + b, 0);

  const codingScoreBreakdown: Record<string, number> = {
    'LeetCode Score': student.coding.leetcode.score,
    'Codeforces Score': student.coding.codeforces.score,
    'CodeChef Score': student.coding.codechef.score,
  };

  const githubScoreBreakdown: Record<string, number> = {
    'Repository Count': Math.min(100, (student.github.repositories / 60) * 100),
    'Stars': Math.min(100, (student.github.stars / 1000) * 100),
    'Commit Activity': Math.min(100, student.github.commitCount / 30),
    'Contribution Consistency': student.github.contributionConsistency,
    'Language Diversity': Math.min(100, student.github.languages.length * 20),
  };

  const semanticScoreBreakdown: Record<string, number> = {
    'Resume-JD Similarity': Math.round(60 + Math.random() * 30),
    'Projects-JD Relevance': Math.round(50 + Math.random() * 40),
    'GitHub-JD Alignment': Math.round(40 + Math.random() * 50),
    'Skills Embedding Match': Math.round(70 + Math.random() * 25),
  };
  const semanticScore = Math.round(
    Object.values(semanticScoreBreakdown).reduce((a, b) => a + b, 0) / 4,
  );

  const eligible =
    student.education.cgpa >= MOCK_JD.minCGPA
    && student.education.specialization !== 'Electronics & Communication'
    && missingMandatory.length === 0;

  const mlScore = 0;
  const finalScore = Math.round(w1 * ruleScore + w2 * semanticScore + w3 * mlScore);

  return {
    rank: 0,
    student,
    eligible,
    scores: {
      ruleScore,
      semanticScore,
      mlScore,
      finalScore,
      w1,
      w2,
      w3,
      matchedSkills: skillMatch,
      missingSkills: missingMandatory,
      ruleScoreBreakdown,
      codingScoreBreakdown,
      githubScoreBreakdown,
      semanticScoreBreakdown,
      explanation:
        `Candidate scored ${finalScore}/100. `
        + `Rule-based score: ${ruleScore}/100 (weight ${Math.round(w1 * 100)}%). `
        + `Semantic match score: ${semanticScore}/100 (weight ${Math.round(w2 * 100)}%). `
        + `Skill match: ${skillMatch.length}/${MOCK_JD.mandatorySkills.length} mandatory skills matched. `
        + `Missing: ${missingMandatory.length > 0 ? missingMandatory.join(', ') : 'none'}. `
        + `Coding strength: ${student.coding.codingStrength}/100. `
        + `GitHub activity: ${student.github.score}/100.`,
    },
  };
}

export const MOCK_RANKINGS: CandidateRanking[] = BASE_STUDENTS
  .map(computeFinalScore)
  .filter((c) => c.eligible)
  .sort((a, b) => b.scores.finalScore - a.scores.finalScore)
  .map((c, i) => ({ ...c, rank: i + 1 }));

export const MOCK_STUDENT = BASE_STUDENTS[0];
