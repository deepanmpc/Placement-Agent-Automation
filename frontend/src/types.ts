export interface PersonalInfo {
  name: string;
  email: string;
  phone: string;
  linkedin: string;
  github: string;
  location: string;
}

export interface Education {
  institution: string;
  degree: string;
  specialization: string;
  cgpa: number;
  startYear: number;
  endYear: number;
}

export interface Skills {
  programming_languages: string[];
  frameworks: string[];
  databases: string[];
  cloud: string[];
  devops: string[];
  tools: string[];
  other: string[];
}

export interface Project {
  title: string;
  description: string;
  technologies: string[];
  url: string;
}

export interface Experience {
  company: string;
  role: string;
  duration: string;
  description: string;
}

export interface Certification {
  name: string;
  issuer: string;
  year: number;
}

export interface Achievement {
  title: string;
  description: string;
}

export interface GitHubData {
  repositories: number;
  stars: number;
  forks: number;
  languages: string[];
  commitCount: number;
  contributionConsistency: number;
  openSourceActivity: string[];
  score: number;
}

export interface LeetCodeData {
  easySolved: number;
  mediumSolved: number;
  hardSolved: number;
  contestRating: number;
  contestHistory: number;
  score: number;
}

export interface CodeforcesData {
  rating: number;
  contestParticipation: number;
  problemsSolved: number;
  score: number;
}

export interface CodeChefData {
  rating: number;
  contestParticipation: number;
  problemsSolved: number;
  score: number;
}

export interface CodingPlatformData {
  leetcode: LeetCodeData;
  codeforces: CodeforcesData;
  codechef: CodeChefData;
  codingStrength: number;
}

export interface Student {
  id: string;
  personalInfo: PersonalInfo;
  education: Education;
  skills: string[];
  projects: Project[];
  experience: Experience[];
  certifications: Certification[];
  achievements: Achievement[];
  github: GitHubData;
  coding: CodingPlatformData;
  aptitudeScore: number;
  communicationScore: number;
}

export interface ScoreBreakdown {
  ruleScore: number;
  semanticScore: number;
  mlScore: number;
  finalScore: number;
  w1: number;
  w2: number;
  w3: number;
  matchedSkills: string[];
  missingSkills: string[];
  ruleScoreBreakdown: Record<string, number>;
  codingScoreBreakdown: Record<string, number>;
  githubScoreBreakdown: Record<string, number>;
  semanticScoreBreakdown: Record<string, number>;
  explanation: string;
}

export interface CandidateRanking {
  rank: number;
  student: Student;
  eligible: boolean;
  scores: ScoreBreakdown;
}

export interface PipelineStage {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'pending' | 'future';
}

export interface JDRequirements {
  title: string;
  company: string;
  description: string;
  minCGPA: number;
  allowedBranches: string[];
  maxBacklogs: number;
  graduationYear: number;
  mandatorySkills: string[];
  preferredSkills: string[];
  minCodingScore: number;
}

export type PageView = 'upload' | 'dashboard' | 'jd-input' | 'candidates' | 'student' | 'analytics' | 'scoring-config';
