export interface Profile {
  student_uuid: string;
  personal_info: {
    name: string;
    email: string;
    phone: string;
    linkedin_url: string;
    github_url: string;
    portfolio_url: string;
    location: string;
    leetcode_username: string;
    codeforces_username: string;
    codechef_username: string;
    id_number?: string;
  };
  education: {
    college: string;
    degree: string;
    branch: string;
    cgpa: number;
    graduation_year: number;
  };
  skills: {
    programming_languages: string[];
    frameworks: string[];
    databases: string[];
    cloud: string[];
    tools: string[];
    all_skills: string[];
  };
  projects: {
    title: string;
    description: string;
    technologies: string[];
    github_link: string;
  }[];
  github: {
    username: string;
    public_repos: number;
    followers: number;
    following: number;
    total_stars: number;
    languages: string[];
    commit_frequency: number;
    activity_score: number;
    contribution_consistency: number;
  };
  leetcode: {
    username: string;
    rating: number;
    ranking: number;
    easy_solved: number;
    medium_solved: number;
    hard_solved: number;
    total_solved: number;
    contests_participated?: number;
  };
  codeforces: {
    username: string;
    rating: number;
    max_rating: number;
    rank: string;
    contests: number;
    solved_count: number;
  };
  codechef: {
    username: string;
    rating: number;
    stars: string;
    contests: number;
    solved_count: number;
  };
  metadata: {
    ingested_at: string;
    sources_collected: string[];
    errors: string[];
  };
  ranking?: any;
}
