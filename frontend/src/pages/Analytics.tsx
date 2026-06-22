import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, 
  PieChart, Pie, Cell, Legend
} from 'recharts';

interface Candidate {
  uuid: string;
  name: string;
  score: number;
  cgpa: number | null;
}

interface AnalyticsData {
  overview: {
    total_students: number;
    average_cgpa: number;
  };
  leetcode_insights: {
    avg_rating: number;
    max_rating: number;
    total_easy: number;
    total_medium: number;
    total_hard: number;
    total_solved: number;
  };
  codeforces_insights: {
    avg_rating: number;
    max_rating: number;
    total_solved: number;
  };
  codechef_insights: {
    avg_rating: number;
    max_rating: number;
  };
  github_insights: {
    total_stars: number;
    total_commits_1yr: number;
    total_repos: number;
  };
  platform_engagement: { name: string; value: number }[];
  skills: {
    languages: { name: string; value: number }[];
    frameworks: { name: string; value: number }[];
    tools: { name: string; value: number }[];
  };
  branch_distribution: { name: string; value: number }[];
  batch_distribution: { name: string; value: number }[];
  top_candidates: Candidate[];
}

const COLORS = ['#22c55e', '#eab308', '#3b82f6', '#ec4899', '#a855f7', '#f97316'];
const LC_COLORS = ['#22c55e', '#eab308', '#ef4444']; // Easy, Medium, Hard

const Analytics = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/analytics')
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching analytics:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="p-8 text-center" style={{ color: 'var(--text-secondary)' }}>Loading advanced analytics...</div>;
  }

  if (!data) {
    return <div className="p-8 text-center" style={{ color: 'var(--color-danger)' }}>Failed to load analytics data.</div>;
  }

  const lcProblemData = [
    { name: 'Easy', value: data.leetcode_insights.total_easy },
    { name: 'Medium', value: data.leetcode_insights.total_medium },
    { name: 'Hard', value: data.leetcode_insights.total_hard }
  ];

  return (
    <div className="analytics-container animate-fade-in" style={{ padding: '2rem' }}>
      <div className="header-section" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>Advanced Batch Analytics</h1>
        <p style={{ color: 'var(--text-secondary)', margin: '0.5rem 0 0 0' }}>Comprehensive insights across candidate performance, skills, and engagement</p>
      </div>

      {/* OVERVIEW CARDS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--text-primary)' }}>{data.overview.total_students}</div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Total Students Evaluated</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--text-primary)' }}>{data.overview.average_cgpa}</div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Batch Avg CGPA</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--text-primary)' }}>{data.github_insights.total_commits_1yr}</div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Total Commits (Last 1Yr)</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--color-warning)' }}>{data.leetcode_insights.total_solved}</div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Total LeetCode Problems Solved</div>
        </div>
      </div>

      {/* PLATFORM METRICS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card" style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)' }}>LeetCode Highlights</h3>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div><span style={{color: 'var(--text-secondary)'}}>Avg Rating:</span> <span style={{fontWeight: 'bold'}}>{data.leetcode_insights.avg_rating}</span></div>
            <div><span style={{color: 'var(--text-secondary)'}}>Max Rating:</span> <span style={{fontWeight: 'bold', color: 'var(--color-warning)'}}>{data.leetcode_insights.max_rating}</span></div>
          </div>
          <div style={{ height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={lcProblemData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={5} dataKey="value" nameKey="name">
                  {lcProblemData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={LC_COLORS[index % LC_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', borderRadius: '8px' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card" style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)' }}>Codeforces & CodeChef</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', height: '100%' }}>
            <div style={{ textAlign: 'center', alignSelf: 'center' }}>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Codeforces Max Rating</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--color-danger)' }}>{data.codeforces_insights.max_rating}</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '1rem' }}>Avg: {data.codeforces_insights.avg_rating}</div>
            </div>
            <div style={{ textAlign: 'center', alignSelf: 'center', borderLeft: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>CodeChef Max Rating</div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#8b5cf6' }}>{data.codechef_insights.max_rating}</div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '1rem' }}>Avg: {data.codechef_insights.avg_rating}</div>
            </div>
          </div>
        </div>

        <div className="card" style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-primary)' }}>GitHub Highlights</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem', height: '100%', alignContent: 'center' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{color: 'var(--text-secondary)'}}>Total Stars</span>
              <span style={{fontWeight: 'bold', color: '#eab308'}}>{data.github_insights.total_stars} ★</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border-color)' }}>
              <span style={{color: 'var(--text-secondary)'}}>Public Repos</span>
              <span style={{fontWeight: 'bold'}}>{data.github_insights.total_repos}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0' }}>
              <span style={{color: 'var(--text-secondary)'}}>Platform Engagement</span>
              <span style={{fontWeight: 'bold'}}>{data.platform_engagement.find(p => p.name === 'GitHub')?.value} Students</span>
            </div>
          </div>
        </div>
      </div>

      {/* SKILLS BREAKDOWN */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '2rem', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
        <h3 style={{ margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Technical Skill Distribution</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem' }}>
          
          <div style={{ height: 250 }}>
            <h4 style={{ textAlign: 'center', margin: '0 0 1rem 0', color: 'var(--text-secondary)' }}>Top Languages</h4>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.skills.languages} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border-color)" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" stroke="var(--text-secondary)" width={80} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)' }} />
                <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div style={{ height: 250 }}>
            <h4 style={{ textAlign: 'center', margin: '0 0 1rem 0', color: 'var(--text-secondary)' }}>Top Frameworks</h4>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.skills.frameworks} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border-color)" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" stroke="var(--text-secondary)" width={80} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)' }} />
                <Bar dataKey="value" fill="#ec4899" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div style={{ height: 250 }}>
            <h4 style={{ textAlign: 'center', margin: '0 0 1rem 0', color: 'var(--text-secondary)' }}>Top Tools & Cloud</h4>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.skills.tools} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border-color)" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" stroke="var(--text-secondary)" width={80} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)' }} />
                <Bar dataKey="value" fill="#10b981" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '2rem' }}>
        
        {/* BRANCH DISTRIBUTION */}
        <div className="card" style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', color: 'var(--text-primary)', textAlign: 'center' }}>Branch Distribution</h3>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.branch_distribution} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value" nameKey="name">
                  {data.branch_distribution.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', borderRadius: '8px' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* TOP CANDIDATES LEADERBOARD */}
        <div className="card" style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Top Candidates Overview</h3>
          <div style={{ overflowY: 'auto', flex: 1, paddingRight: '0.5rem', maxHeight: '300px' }}>
            {data.top_candidates.map((c, idx) => (
              <div key={c.uuid} style={{ 
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
                padding: '0.75rem 0', borderBottom: '1px solid var(--border-color)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ 
                    width: '32px', height: '32px', borderRadius: '50%', 
                    backgroundColor: idx < 3 ? 'var(--color-primary)' : 'var(--bg-secondary)',
                    color: idx < 3 ? 'white' : 'var(--text-secondary)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 'bold', fontSize: '0.9rem'
                  }}>
                    {idx + 1}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>CGPA: {c.cgpa || 'N/A'}</div>
                  </div>
                </div>
                <div style={{ fontWeight: 700, color: 'var(--color-success)', fontSize: '1.1rem' }}>{c.score} <span style={{fontSize:'0.7rem', color:'var(--text-secondary)'}}>pts</span></div>
              </div>
            ))}
            {data.top_candidates.length === 0 && (
               <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '1rem' }}>No candidates found</div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Analytics;
