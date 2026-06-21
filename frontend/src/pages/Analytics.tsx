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
    avg_lc_rating: number;
    avg_cf_rating: number;
    avg_cc_rating: number;
  };
  platform_engagement: { name: string; value: number }[];
  top_skills: { name: string; value: number }[];
  branch_distribution: { name: string; value: number }[];
  batch_distribution: { name: string; value: number }[];
  top_candidates: Candidate[];
}

const COLORS = ['#22c55e', '#eab308', '#3b82f6', '#ec4899', '#a855f7', '#f97316'];

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

  return (
    <div className="analytics-container animate-fade-in" style={{ padding: '2rem' }}>
      <div className="header-section" style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>Batch Analytics</h1>
        <p style={{ color: 'var(--text-secondary)', margin: '0.5rem 0 0 0' }}>Comprehensive insights across the candidate pool</p>
      </div>

      {/* OVERVIEW CARDS */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--text-primary)' }}>{data.overview.total_students}</div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Total Students</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--text-primary)' }}>{data.overview.average_cgpa}</div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Avg CGPA</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--color-warning)' }}>{data.overview.avg_lc_rating}</div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Avg LeetCode Rating</div>
        </div>
        <div className="card" style={{ padding: '1.5rem', textAlign: 'center', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '2.5rem', fontWeight: '800', color: 'var(--color-danger)' }}>{data.overview.avg_cf_rating}</div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Avg Codeforces Rating</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        
        {/* PLATFORM ENGAGEMENT */}
        <div className="card" style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Platform Engagement</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.platform_engagement} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border-color)" />
                <XAxis type="number" stroke="var(--text-secondary)" />
                <YAxis dataKey="name" type="category" stroke="var(--text-secondary)" />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', borderRadius: '8px' }}
                  itemStyle={{ color: 'var(--text-primary)' }}
                />
                <Bar dataKey="value" fill="var(--color-primary)" radius={[0, 4, 4, 0]}>
                  {data.platform_engagement.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* TOP SKILLS */}
        <div className="card" style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Most Common Skills</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.top_skills} margin={{ bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
                <XAxis dataKey="name" stroke="var(--text-secondary)" angle={-45} textAnchor="end" interval={0} />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', borderRadius: '8px' }}
                  itemStyle={{ color: 'var(--text-primary)' }}
                />
                <Bar dataKey="value" fill="var(--color-success)" radius={[4, 4, 0, 0]} />
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

        {/* BATCH DISTRIBUTION */}
        <div className="card" style={{ padding: '1.5rem', backgroundColor: 'var(--bg-card)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <h3 style={{ margin: '0 0 1.5rem 0', color: 'var(--text-primary)', textAlign: 'center' }}>Batch Distribution</h3>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.batch_distribution} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value" nameKey="name">
                  {data.batch_distribution.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
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
          <h3 style={{ margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Top Candidates</h3>
          <div style={{ overflowY: 'auto', flex: 1, paddingRight: '0.5rem', maxHeight: '250px' }}>
            {data.top_candidates.map((c, idx) => (
              <div key={c.uuid} style={{ 
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
                padding: '0.75rem 0', borderBottom: '1px solid var(--border-color)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <div style={{ 
                    width: '28px', height: '28px', borderRadius: '50%', 
                    backgroundColor: idx < 3 ? 'var(--color-primary)' : 'var(--bg-secondary)',
                    color: idx < 3 ? 'white' : 'var(--text-secondary)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 'bold', fontSize: '0.8rem'
                  }}>
                    {idx + 1}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.name}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>CGPA: {c.cgpa || 'N/A'}</div>
                  </div>
                </div>
                <div style={{ fontWeight: 700, color: 'var(--color-success)' }}>{c.score} pts</div>
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
