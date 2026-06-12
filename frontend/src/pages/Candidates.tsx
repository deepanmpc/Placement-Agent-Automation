import { useEffect, useState } from 'react';
import type { PageView } from '../types';
import type { Profile } from '../api';

interface Props {
  onSelect: (studentId: string) => void;
  onNavigate: (page: PageView) => void;
}

export default function Candidates({ onSelect, onNavigate }: Props) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [deleting, setDeleting] = useState(false);

  const fetchProfiles = () => {
    fetch('http://localhost:8000/profiles')
      .then(res => res.json())
      .then(data => {
        setProfiles(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchProfiles();
  }, []);

  const handleEnrich = async () => {
    setEnriching(true);
    try {
      const payload = selectedIds.size > 0 
        ? { student_uuids: Array.from(selectedIds), batch_size: selectedIds.size }
        : { batch_size: 10 };
        
      const response = await fetch('http://localhost:8000/profiles/batch-enrich', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      alert(`Successfully extracted data for ${data.enriched} profiles! Errors: ${data.errors.length}`);
      fetchProfiles();
    } catch (err) {
      console.error(err);
      alert('Failed to extract profile data.');
    } finally {
      setEnriching(false);
    }
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(new Set(profiles.map(p => p.student_uuid)));
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelect = (id: string, checked: boolean) => {
    const newSet = new Set(selectedIds);
    if (checked) newSet.add(id);
    else newSet.delete(id);
    setSelectedIds(newSet);
  };

  const handleDeleteSelected = async () => {
    if (!window.confirm(`Are you sure you want to delete ${selectedIds.size} profiles?`)) return;
    
    setDeleting(true);
    try {
      const promises = Array.from(selectedIds).map(id => 
        fetch(`http://localhost:8000/profiles/${id}`, { method: 'DELETE' })
      );
      await Promise.all(promises);
      setSelectedIds(new Set());
      fetchProfiles();
    } catch (err) {
      console.error(err);
      alert('Failed to delete some profiles.');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return <div className="page"><div className="page-header"><h1>Loading profiles...</h1></div></div>;
  }

  return (
    <div className="page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Ingested Profiles Dashboard</h1>
          <p className="page-subtitle">
            {profiles.length} total students ingested
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          {selectedIds.size > 0 && (
            <button 
              className="btn btn-primary" 
              style={{ backgroundColor: '#ef4444', borderColor: '#ef4444' }}
              onClick={handleDeleteSelected}
              disabled={deleting}
            >
              {deleting ? 'Deleting...' : `Delete Selected (${selectedIds.size})`}
            </button>
          )}
          <button 
            className="btn btn-primary" 
            onClick={handleEnrich} 
            disabled={enriching}
          >
            {enriching ? 'Enriching...' : 'Extract Coding & GitHub Data'}
          </button>
        </div>
      </div>

      <div className="ranking-summary">
        <div className="summary-stat">
          <span className="stat-value">{profiles.length}</span>
          <span className="stat-label">Total Students</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value">{profiles.filter(p => p.github?.public_repos > 0).length}</span>
          <span className="stat-label">With GitHub Data</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value">{profiles.filter(p => p.leetcode?.total_solved > 0).length}</span>
          <span className="stat-label">With LeetCode Data</span>
        </div>
      </div>

      <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <input 
          type="checkbox" 
          checked={profiles.length > 0 && selectedIds.size === profiles.length}
          onChange={handleSelectAll}
          id="selectAll"
        />
        <label htmlFor="selectAll">Select All</label>
      </div>

      <div className="candidates-list">
        {profiles.map((p) => (
          <div 
            key={p.student_uuid} 
            className="candidate-card" 
            style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}
          >
            <input 
              type="checkbox" 
              checked={selectedIds.has(p.student_uuid)}
              onChange={(e) => handleSelect(p.student_uuid, e.target.checked)}
              style={{ transform: 'scale(1.2)' }}
            />
            <div 
              style={{ flex: 1, display: 'flex', justifyContent: 'space-between', cursor: 'pointer' }}
              onClick={() => {
                onSelect(p.student_uuid);
                onNavigate('student');
              }}
            >
              <div className="candidate-info">
                <h3 className="candidate-name">
                  {p.personal_info.name || 'Unknown Candidate'} {p.personal_info.id_number ? `(${p.personal_info.id_number})` : ''}
                </h3>
                <p className="candidate-meta">
                  {p.education.college} &middot; {p.education.branch} &middot;
                  CGPA {p.education.cgpa || 'N/A'}
                </p>
                <div className="candidate-tags">
                  {p.skills.all_skills.slice(0, 5).map((s) => (
                    <span key={s} className="tag tag-match">{s}</span>
                  ))}
                </div>
              </div>
              <div className="candidate-scores">
                <div className="score-mini">
                  <span>GH Repos: {p.github.public_repos}</span>
                  <span>LC Solved: {p.leetcode.total_solved}</span>
                  <span>CF Rating: {p.codeforces.rating}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        {profiles.length === 0 && <p>No profiles ingested yet. Upload some resumes!</p>}
      </div>
    </div>
  );
}
