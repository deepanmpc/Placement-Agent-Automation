import { useEffect, useState } from 'react';
import type { PageView } from '../types';
import type { Profile } from '../api';
import type { ScoringMode } from '../components/ScoringSettings';

const MODE_LABELS: Record<ScoringMode, string> = {
  dsa_mode: 'DSA Mode',
  github_mode: 'GH Mode',
  custom: 'Custom',
};

interface Props {
  onSelect: (studentId: string) => void;
  onNavigate: (page: PageView) => void;
  scoringMode: ScoringMode;
}

export default function Candidates({ onSelect, onNavigate, scoringMode }: Props) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [deleting, setDeleting] = useState(false);

  // Search & Filtering States
  const [searchQuery, setSearchQuery] = useState('');
  const [minScore, setMinScore] = useState<number>(0);
  const [selectedBatch, setSelectedBatch] = useState<string>('all');

  const getCandidateScore = (p: Profile): number => {
    if (!p.ranking) return 0;
    return scoringMode === 'dsa_mode' ? p.ranking.overall_dsa_mode
      : scoringMode === 'github_mode' ? p.ranking.overall_github_mode
      : p.ranking.custom_score ?? p.ranking.total_technical_score;
  };

  const uniqueBatches = Array.from(new Set(profiles.map(p => p.education?.graduation_year).filter(Boolean))).sort();

  const filteredProfiles = profiles.filter(p => {
    const name = (p.personal_info.name || '').toLowerCase();
    const id = (p.personal_info.id_number || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    const matchesSearch = name.includes(query) || id.includes(query);

    const score = getCandidateScore(p);
    const matchesScore = score >= minScore;

    const batch = p.education?.graduation_year?.toString() || '';
    const matchesBatch = selectedBatch === 'all' || batch === selectedBatch;

    return matchesSearch && matchesScore && matchesBatch;
  });

  const allFilteredSelected = filteredProfiles.length > 0 && filteredProfiles.every(p => selectedIds.has(p.student_uuid));

  const fetchProfiles = () => {
    fetch('http://localhost:8000/profiles', { cache: 'no-store' })
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

  const handleSelectAll = () => {
    if (allFilteredSelected) {
      const newSet = new Set(selectedIds);
      filteredProfiles.forEach(p => newSet.delete(p.student_uuid));
      setSelectedIds(newSet);
    } else {
      const newSet = new Set(selectedIds);
      filteredProfiles.forEach(p => newSet.add(p.student_uuid));
      setSelectedIds(newSet);
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

      <div className="ranking-summary" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
        <div className="summary-stat">
          <span className="stat-value">{profiles.length}</span>
          <span className="stat-label">Total Students</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value">{profiles.filter(p => p.github?.public_repos > 0 || p.github?.total_stars > 0).length}</span>
          <span className="stat-label">With GitHub Data</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value">{profiles.filter(p => p.leetcode?.total_solved > 0).length}</span>
          <span className="stat-label">With LeetCode Data</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value">{profiles.filter(p => p.codeforces?.rating > 0 || p.codeforces?.solved_count > 0).length}</span>
          <span className="stat-label">With Codeforces Data</span>
        </div>
        <div className="summary-stat">
          <span className="stat-value">{profiles.filter(p => p.codechef?.rating > 0 || p.codechef?.solved_count > 0).length}</span>
          <span className="stat-label">With CodeChef Data</span>
        </div>
      </div>

      {/* Search & Filter Section */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1.25rem',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border)',
        borderRadius: '12px',
        padding: '1.25rem',
        marginBottom: '1.5rem',
        boxShadow: 'var(--shadow-sm)'
      }}>
        {/* Search */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Search Candidate
          </label>
          <input 
            type="text"
            placeholder="Search name or ID..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            style={{
              padding: '0.5rem 0.75rem',
              borderRadius: '8px',
              border: '1px solid var(--border)',
              background: 'var(--bg)',
              color: 'var(--text-primary)',
              fontSize: '0.82rem',
              outline: 'none',
            }}
          />
        </div>

        {/* Score filter */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Min Score
            </label>
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent)' }}>
              {minScore} pts
            </span>
          </div>
          <input 
            type="range"
            min={0}
            max={100}
            step={1}
            value={minScore}
            onChange={e => setMinScore(Number(e.target.value))}
            style={{
              width: '100%',
              accentColor: 'var(--accent)',
              cursor: 'pointer',
              marginTop: '0.35rem'
            }}
          />
        </div>

        {/* Batch filter */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Graduation Batch
          </label>
          <select
            value={selectedBatch}
            onChange={e => setSelectedBatch(e.target.value)}
            style={{
              padding: '0.5rem 0.75rem',
              borderRadius: '8px',
              border: '1px solid var(--border)',
              background: 'var(--bg)',
              color: 'var(--text-primary)',
              fontSize: '0.82rem',
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value="all">All Batches</option>
            {uniqueBatches.map(batch => (
              <option key={batch} value={batch.toString()}>{batch} Batch</option>
            ))}
          </select>
        </div>

        {/* Clear Filters Button */}
        {(searchQuery || minScore > 0 || selectedBatch !== 'all') && (
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              onClick={() => {
                setSearchQuery('');
                setMinScore(0);
                setSelectedBatch('all');
              }}
              style={{
                width: '100%',
                padding: '0.5rem 0.75rem',
                background: 'transparent',
                border: '1px dashed var(--color-danger)',
                color: 'var(--color-danger)',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>

      <div 
        onClick={handleSelectAll}
        style={{
          marginBottom: '1.25rem',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.6rem',
          cursor: 'pointer',
          padding: '0.45rem 0.85rem',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          fontSize: '0.82rem',
          fontWeight: 600,
          color: 'var(--text-secondary)',
          userSelect: 'none',
          boxShadow: 'var(--shadow-sm)',
          transition: 'all 0.2s ease'
        }}
      >
        <div style={{
          width: '18px',
          height: '18px',
          borderRadius: '5px',
          border: `2px solid ${allFilteredSelected ? 'var(--accent)' : 'var(--border)'}`,
          background: allFilteredSelected ? 'var(--accent)' : 'transparent',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.2s ease',
          flexShrink: 0
        }}>
          {allFilteredSelected && (
            <span style={{ color: '#fff', fontSize: '0.65rem', fontWeight: 'bold' }}>✓</span>
          )}
        </div>
        <span>Select All Candidates ({filteredProfiles.length})</span>
      </div>

      <div className="candidates-list">
        {filteredProfiles.map((p) => (
          <div 
            key={p.student_uuid} 
            className="candidate-card" 
            style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', padding: '1rem 1.25rem' }}
          >
            {/* Custom Checkbox */}
            <div 
              onClick={(e) => {
                e.stopPropagation();
                handleSelect(p.student_uuid, !selectedIds.has(p.student_uuid));
              }}
              style={{
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '22px',
                height: '22px',
                borderRadius: '6px',
                border: `2px solid ${selectedIds.has(p.student_uuid) ? 'var(--accent)' : 'var(--border)'}`,
                background: selectedIds.has(p.student_uuid) ? 'var(--accent)' : 'transparent',
                boxShadow: selectedIds.has(p.student_uuid) ? '0 0 10px rgba(99, 102, 241, 0.25)' : 'none',
                transition: 'all 0.2s ease',
                flexShrink: 0
              }}
            >
              {selectedIds.has(p.student_uuid) && (
                <span style={{ color: '#fff', fontSize: '0.75rem', fontWeight: 'bold', lineHeight: 1 }}>✓</span>
              )}
            </div>

            <div 
              style={{ flex: 1, display: 'flex', justifyContent: 'space-between', cursor: 'pointer', alignItems: 'center' }}
              onClick={() => {
                onSelect(p.student_uuid);
                onNavigate('student');
              }}
            >
              <div className="candidate-info" style={{ display: 'flex', alignItems: 'center' }}>
                <h3 className="candidate-name" style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                  {p.personal_info.name || 'Unknown Candidate'} {p.personal_info.id_number ? `(${p.personal_info.id_number})` : ''}
                </h3>
              </div>
              <div className="candidate-scores" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.4rem' }}>
                {p.ranking ? (
                  <>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textAlign: 'right', marginBottom: '0.1rem' }}>
                      {MODE_LABELS[scoringMode]}
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary)', lineHeight: 1 }}>
                      {scoringMode === 'dsa_mode' ? p.ranking.overall_dsa_mode
                        : scoringMode === 'github_mode' ? p.ranking.overall_github_mode
                        : p.ranking.custom_score ?? p.ranking.total_technical_score}
                      <span style={{ fontSize: '0.85rem', opacity: 0.6, fontWeight: 400 }}>/100</span>
                    </div>
                    <div className="score-mini" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'flex-end', marginTop: '0.25rem' }}>
                      {(p.ranking.lc_score ?? 0) > 0 && <span>LC: {p.ranking.lc_score}</span>}
                      {(p.ranking.cc_score ?? 0) > 0 && <span>CC: {p.ranking.cc_score}</span>}
                      {(p.ranking.cf_score ?? 0) > 0 && <span>CF: {p.ranking.cf_score}</span>}
                      {(p.ranking.github_score_total ?? 0) > 0 && <span>GH: {p.ranking.github_score_total}</span>}
                    </div>
                  </>
                ) : (
                  <div className="score-mini">
                    <span>GH Repos: {p.github.public_repos}</span>
                    <span>LC Solved: {p.leetcode.total_solved}</span>
                    <span>CF Rating: {p.codeforces.rating}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {profiles.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', textAlign: 'center', padding: '2rem' }}>
            No profiles ingested yet. Upload some resumes!
          </p>
        ) : filteredProfiles.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', textAlign: 'center', padding: '2rem' }}>
            No profiles match the search or filter criteria.
          </p>
        ) : null}
      </div>
    </div>
  );
}
