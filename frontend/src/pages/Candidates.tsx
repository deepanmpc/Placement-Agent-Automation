import { useEffect, useState, useRef } from 'react';
import { utils, writeFile } from 'xlsx';
import type { PageView } from '../types';
import type { Profile } from '../api';
import type { ScoringMode, CustomWeights } from '../components/ScoringSettings';

const MODE_LABELS: Record<ScoringMode, string> = {
  dsa_mode: 'DSA Mode',
  github_mode: 'GH Mode',
  fitment_mode: 'Fitment Mode',
  custom: 'Custom',
};

const getBatchLabel = (year: number | string | undefined | null): string => {
  if (!year) return '';
  const yearStr = year.toString();
  if (yearStr === '2023') return 'Y23';
  if (yearStr === '2024') return 'Y24';
  if (yearStr === '2025') return 'Y25';
  if (yearStr === '2026') return 'Y26';
  if (yearStr.length >= 2) {
    return 'Y' + yearStr.slice(-2);
  }
  return 'Y' + yearStr;
};

interface Props {
  onSelect: (studentId: string) => void;
  onNavigate: (page: PageView) => void;
  scoringMode: ScoringMode;
  customWeights: CustomWeights;
}

export default function Candidates({ onSelect, onNavigate, scoringMode, customWeights }: Props) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [deleting, setDeleting] = useState(false);

  // Search & Filtering States
  const [searchQuery, setSearchQuery] = useState('');
  const [minScore, setMinScore] = useState<number>(0);
  const [activeBatch, setActiveBatch] = useState<string | null>('all');
  const [missingFilter, setMissingFilter] = useState<string | null>(null);
  const [showExportPreview, setShowExportPreview] = useState(false);
  const [exportPreviewData, setExportPreviewData] = useState<any[]>([]);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const getCandidateScore = (p: Profile): number => {
    if (!p.ranking) return 0;
    if (scoringMode === 'fitment_mode' && p.ranking?.fitment_score !== undefined) {
      return p.ranking.fitment_score;
    }
    return scoringMode === 'dsa_mode' ? p.ranking.overall_dsa_mode
      : scoringMode === 'github_mode' ? p.ranking.overall_github_mode
      : p.ranking.custom_score ?? p.ranking.total_technical_score;
  };



  const filteredProfiles = profiles.filter(p => {
    const name = (p.personal_info.name || '').toLowerCase();
    const id = (p.personal_info.id_number || '').toLowerCase();
    const query = searchQuery.toLowerCase();
    const matchesSearch = name.includes(query) || id.includes(query);

    const score = getCandidateScore(p);
    const matchesScore = score >= minScore;

    const batch = p.education?.graduation_year?.toString() || '';
    const matchesBatch = !activeBatch || activeBatch === 'all' || batch === activeBatch || batch === '';

    let matchesMissing = true;
    if (missingFilter === 'github') matchesMissing = !(p.github?.public_repos > 0 || p.github?.total_stars > 0);
    if (missingFilter === 'leetcode') matchesMissing = !(p.leetcode?.total_solved > 0);
    if (missingFilter === 'codeforces') matchesMissing = !(p.codeforces?.rating > 0 || p.codeforces?.solved_count > 0);
    if (missingFilter === 'codechef') matchesMissing = !(p.codechef?.rating > 0 || p.codechef?.solved_count > 0);

    return matchesSearch && matchesScore && matchesBatch && matchesMissing;
  }).sort((a, b) => getCandidateScore(b) - getCandidateScore(a));

  const allFilteredSelected = filteredProfiles.length > 0 && filteredProfiles.every(p => selectedIds.has(p.student_uuid));

  const fetchProfiles = () => {
    let query = `?lc_w=${customWeights.lc}&cc_w=${customWeights.cc}&cf_w=${customWeights.cf}&gh_w=${customWeights.gh}&sm_w=${customWeights.sm || 0}`;
    const activeJd = localStorage.getItem('active_jd');
    if (activeJd) {
      query += `&job_description=${encodeURIComponent(activeJd)}`;
    }
    fetch(`http://localhost:8000/profiles${query}`, { cache: 'no-store' })
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
  }, [customWeights]);

  const [extractionJob, setExtractionJob] = useState<{ active: boolean; status?: string; total: number; completed: number; estimated_seconds: number } | null>(null);

  const wasActiveRef = useRef(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    const pollStatus = async () => {
      try {
        const res = await fetch('http://localhost:8000/profiles/extraction-job/status');
        const data = await res.json();
        
        if (data.active) {
          setEnriching(true);
          setExtractionJob(data);
          wasActiveRef.current = true;
        } else {
          setExtractionJob(data);
          if (wasActiveRef.current) {
            wasActiveRef.current = false;
            setEnriching(false);
            if (data.status === "COMPLETED") {
               alert('Extraction job completed successfully!');
            }
            fetchProfiles();
          }
        }
      } catch (err) {}
    };

    pollStatus();
    interval = setInterval(pollStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const [showResumeModal, setShowResumeModal] = useState(false);

  const startEnrich = async (reset: boolean) => {
    setShowResumeModal(false);
    setEnriching(true);
    wasActiveRef.current = true;
    setExtractionJob({ active: true, status: "IN_PROGRESS", total: 1, completed: 0, estimated_seconds: 0 });
    
    try {
      const payload = selectedIds.size > 0 
        ? { student_uuids: Array.from(selectedIds), batch_size: selectedIds.size, reset }
        : { student_uuids: filteredProfiles.map(p => p.student_uuid), batch_size: filteredProfiles.length || 1, reset };

      if (payload.student_uuids.length === 0) {
        alert('No candidates found to extract data for in the current view.');
        setEnriching(false);
        wasActiveRef.current = false;
        setExtractionJob(null);
        return;
      }
        
      await fetch('http://localhost:8000/profiles/batch-enrich', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (err) {
      console.error(err);
      alert('Failed to start extraction.');
      setEnriching(false);
      wasActiveRef.current = false;
      setExtractionJob(null);
    }
  };

  const handleEnrich = () => {
    setShowResumeModal(true);
  };

  const handleCancelEnrich = async () => {
    try {
      await fetch('http://localhost:8000/profiles/extraction-job/cancel', { method: 'POST' });
      setEnriching(false);
      wasActiveRef.current = false;
      setExtractionJob(prev => prev ? { ...prev, active: false, status: "PAUSED" } : null);
      alert('Extraction job paused. You can resume later.');
    } catch (err) {
      console.error(err);
    }
  };

  const handlePreviewExport = () => {
    const exportData = filteredProfiles.map(p => {
      const missing = [];
      if (!(p.github?.public_repos > 0 || p.github?.total_stars > 0)) missing.push('GitHub');
      if (!(p.leetcode?.total_solved > 0)) missing.push('LeetCode');
      if (!(p.codeforces?.rating > 0 || p.codeforces?.solved_count > 0)) missing.push('Codeforces');
      if (!(p.codechef?.rating > 0 || p.codechef?.solved_count > 0)) missing.push('CodeChef');
      
      return {
        'Student Name': p.personal_info.name || 'Unknown',
        'ID Number': p.personal_info.id_number || 'Unknown',
        'Missing Platforms': missing.join(', ') || 'None'
      };
    });
    setExportPreviewData(exportData);
    setShowExportPreview(true);
  };

  const handleConfirmExport = () => {
    const worksheet = utils.json_to_sheet(exportPreviewData);
    const workbook = utils.book_new();
    utils.book_append_sheet(workbook, worksheet, 'Students Data');
    writeFile(workbook, 'Student_Extract.xlsx');
    setShowExportPreview(false);
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



  // Group profiles by batch
  const groupedProfiles: Record<string, Profile[]> = {};
  filteredProfiles.forEach(p => {
    const label = getBatchLabel(p.education?.graduation_year) || 'Unknown Batch';
    const finalLabel = label === 'Unknown Batch' || label.endsWith('Batch') ? label : `${label} Batch`;
    if (!groupedProfiles[finalLabel]) {
      groupedProfiles[finalLabel] = [];
    }
    groupedProfiles[finalLabel].push(p);
  });

  const sortedBatchKeys = Object.keys(groupedProfiles).sort((a, b) => {
    if (a === 'Unknown Batch') return 1;
    if (b === 'Unknown Batch') return -1;
    const numA = parseInt(a.replace(/\D/g, ''), 10) || 0;
    const numB = parseInt(b.replace(/\D/g, ''), 10) || 0;
    return numB - numA;
  });

  const globalRanks = new Map(filteredProfiles.map((p, i) => [p.student_uuid, i + 1]));

  return (
    <div className="page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ flex: '1 1 300px', minWidth: 0 }}>
          <h1>Ingested Profiles Dashboard</h1>
          <p className="page-subtitle" style={{ marginBottom: '0.4rem' }}>
            {profiles.length} total students ingested in {activeBatch === 'all' ? 'All Batches' : activeBatch}
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            <span style={{ padding: '0.2rem 0.5rem', background: 'var(--bg)', borderRadius: '4px', border: '1px solid var(--border)' }}>
              Mode: <span style={{ color: 'var(--accent)' }}>{MODE_LABELS[scoringMode] || scoringMode}</span>
            </span>
            {scoringMode === 'custom' && (
              <span style={{ padding: '0.2rem 0.5rem', background: 'var(--bg)', borderRadius: '4px', border: '1px solid var(--border)' }}>
                Weights: LC {customWeights.lc}% &middot; CC {customWeights.cc}% &middot; CF {customWeights.cf}% &middot; GH {customWeights.gh}% &middot; SM {customWeights.sm || 0}%
              </span>
            )}
          </div>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center' }}>
          <a
            onClick={(e) => { e.preventDefault(); setActiveBatch('all'); }}
            style={{ fontSize: '0.85rem', color: 'var(--accent)', cursor: 'pointer', textDecoration: 'none', fontWeight: 700, marginRight: '0.5rem' }}
            onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
            onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
          >
            All Batches
          </a>
          <a
            onClick={(e) => { e.preventDefault(); onNavigate('jd-input'); }}
            style={{ fontSize: '0.85rem', color: 'var(--accent)', cursor: 'pointer', textDecoration: 'none', fontWeight: 700, marginRight: '1rem' }}
            onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
            onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
          >
            Configure Scoring
          </a>
          {selectedIds.size > 0 && (
            <button 
              className="btn btn-primary" 
              style={{ backgroundColor: '#991111', borderColor: '#991111' }}
              onClick={handleDeleteSelected}
              disabled={deleting}
            >
              {deleting ? 'Deleting...' : `Delete Selected (${selectedIds.size})`}
            </button>
          )}
          <button 
            className="btn btn-primary" 
            onClick={handlePreviewExport} 
            style={{ fontSize: '0.85rem', backgroundColor: '#10b981', borderColor: '#10b981' }}
          >
            Export Displayed Data
          </button>
          {extractionJob?.active ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{
                background: 'var(--surface)',
                padding: '0.4rem 0.8rem',
                borderRadius: '8px',
                border: '1px solid var(--border)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minWidth: '150px'
              }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.2rem' }}>
                  Extracting: {extractionJob.completed} / {extractionJob.total}
                </div>
                <div style={{ width: '100%', backgroundColor: 'var(--border)', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ width: `${(extractionJob.completed / extractionJob.total) * 100}%`, backgroundColor: 'var(--accent)', height: '100%', transition: 'width 0.3s ease' }}></div>
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  ETA: {Math.max(0, Math.round(extractionJob.estimated_seconds))}s
                </div>
              </div>
              <button 
                className="btn btn-primary" 
                onClick={handleCancelEnrich} 
                style={{ fontSize: '0.75rem', backgroundColor: '#ef4444', borderColor: '#ef4444', padding: '0.4rem 0.8rem' }}
              >
                Pause
              </button>
            </div>
          ) : (
            <button 
              className="btn btn-primary" 
              onClick={handleEnrich} 
              disabled={enriching}
              style={{ 
                fontSize: '0.85rem', 
                background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)', 
                border: 'none',
                boxShadow: '0 4px 15px rgba(168, 85, 247, 0.4)',
                color: 'white',
                fontWeight: 800,
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}
            >
              {extractionJob && extractionJob.status === "PAUSED" ? 'Resume Extraction' : 'Extract Coding & GitHub Data'}
            </button>
          )}
        </div>
      </div>

      <div className="ranking-summary" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem' }}>
        <div className="summary-stat" style={{ cursor: 'pointer', border: missingFilter === null ? '2px solid var(--accent)' : '1px solid var(--border)' }} onClick={() => setMissingFilter(null)}>
          <span className="stat-value">{profiles.length}</span>
          <span className="stat-label">Total Students</span>
        </div>
        
        {[
          { key: 'github', label: 'GitHub Data', hasData: (p: Profile) => p.github?.public_repos > 0 || p.github?.total_stars > 0 },
          { key: 'leetcode', label: 'LeetCode Data', hasData: (p: Profile) => p.leetcode?.total_solved > 0 },
          { key: 'codeforces', label: 'Codeforces Data', hasData: (p: Profile) => p.codeforces?.rating > 0 || p.codeforces?.solved_count > 0 },
          { key: 'codechef', label: 'CodeChef Data', hasData: (p: Profile) => p.codechef?.rating > 0 || p.codechef?.solved_count > 0 }
        ].map(platform => {
          const missingCount = profiles.filter(p => !platform.hasData(p)).length;
          const isSelected = missingFilter === platform.key;
          return (
            <div 
              key={platform.key}
              className="summary-stat" 
              style={{ 
                cursor: 'pointer', 
                border: isSelected ? '2px solid var(--color-danger)' : '1px solid var(--border)',
                background: isSelected ? '#ff00000a' : 'var(--card-bg)'
              }}
              onClick={() => setMissingFilter(isSelected ? null : platform.key)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span className="stat-value">{profiles.filter(p => platform.hasData(p)).length}</span>
                  <span className="stat-label">With {platform.label}</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', textAlign: 'right', opacity: 0.8 }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--color-danger)' }}>{missingCount}</span>
                  <span style={{ fontSize: '0.55rem', textTransform: 'uppercase', color: 'var(--color-danger)', fontWeight: 700 }}>Missing</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Symmetric Control Panel (Search, Batch, Score) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1.5rem',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border)',
        borderRadius: '12px',
        padding: '1.25rem',
        marginBottom: '1.5rem',
        boxShadow: 'var(--shadow-sm)',
        alignItems: 'flex-start'
      }}>
        {/* Column 1: Search */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Search Candidate
            </label>
            {(searchQuery !== '' || minScore > 0 || missingFilter !== null) && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setMinScore(0);
                  setMissingFilter(null);
                }}
                style={{
                  background: 'none', border: 'none', color: 'var(--color-danger)',
                  fontSize: '0.72rem', fontWeight: 700, cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.05em'
                }}
              >
                Clear Filters
              </button>
            )}
          </div>
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
              width: '100%'
            }}
          />
        </div>

        {/* Column 2: Batch Switcher */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Graduation Batch
          </label>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            background: 'var(--bg)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            padding: '0.2rem',
            width: '100%',
            justifyContent: 'space-between'
          }}>
            {[
              { value: 'all', label: 'All' },
              { value: '2023', label: 'Y23' },
              { value: '2024', label: 'Y24' },
              { value: '2025', label: 'Y25' },
              { value: '2026', label: 'Y26' }
            ].map(item => {
              const isSelected = activeBatch === item.value;
              return (
                <button
                  key={item.value}
                  onClick={() => setActiveBatch(item.value)}
                  style={{
                    flex: 1,
                    padding: '0.35rem 0',
                    borderRadius: '6px',
                    border: 'none',
                    background: isSelected ? 'var(--accent)' : 'transparent',
                    color: isSelected ? '#fff' : 'var(--text-secondary)',
                    fontSize: '0.8rem',
                    fontWeight: isSelected ? 700 : 600,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Column 3: Score Filter */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
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
              marginTop: '0.45rem'
            }}
          />
        </div>
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

      <div className="candidates-list" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {sortedBatchKeys.map(batchKey => (
          <div key={batchKey} style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              paddingBottom: '0.4rem',
              borderBottom: '1px solid var(--border)',
              margin: '0.5rem 0 0.2rem 0'
            }}>
              <span style={{
                background: 'var(--accent)',
                color: 'white',
                padding: '0.15rem 0.5rem',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: 750,
                textTransform: 'uppercase'
              }}>
                {batchKey}
              </span>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                ({groupedProfiles[batchKey].length} {groupedProfiles[batchKey].length === 1 ? 'candidate' : 'candidates'})
              </span>
            </div>
            
            {groupedProfiles[batchKey].map((p) => (
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
                    boxShadow: selectedIds.has(p.student_uuid) ? '0 0 10px var(--accent-bg)' : 'none',
                    transition: 'all 0.2s ease',
                    flexShrink: 0
                  }}
                >
                  {selectedIds.has(p.student_uuid) && (
                    <span style={{ color: '#fff', fontSize: '0.75rem', fontWeight: 'bold', lineHeight: 1 }}>✓</span>
                  )}
                </div>

                {/* Serial Rank Number */}
                <div style={{
                  fontSize: '1.25rem',
                  fontWeight: 900,
                  color: 'var(--text-tertiary)',
                  width: '32px',
                  textAlign: 'right',
                  marginRight: '0.5rem',
                  fontVariantNumeric: 'tabular-nums'
                }}>
                  #{globalRanks.get(p.student_uuid)}
                </div>

                <div 
                  style={{ flex: 1, display: 'flex', justifyContent: 'space-between', cursor: 'pointer', alignItems: 'center' }}
                  onClick={() => {
                    onSelect(p.student_uuid);
                    onNavigate('student');
                  }}
                >
                  <div className="candidate-info" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <h3 className="candidate-name" style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                      {p.personal_info.name || 'Unknown Candidate'} {p.personal_info.id_number ? `(${p.personal_info.id_number})` : ''}
                    </h3>
                    {p.education?.graduation_year && (
                      <span style={{
                        background: 'var(--bg-secondary)',
                        color: 'var(--accent)',
                        border: '1px solid var(--border)',
                        padding: '0.15rem 0.5rem',
                        borderRadius: '6px',
                        fontSize: '0.7rem',
                        fontWeight: 700
                      }}>
                        {getBatchLabel(p.education.graduation_year)}
                      </span>
                    )}
                  </div>
                  <div className="candidate-scores" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.4rem' }}>
                    {p.ranking ? (
                      <>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textAlign: 'right', marginBottom: '0.1rem' }}>
                          {scoringMode === 'fitment_mode' ? (
                            <span style={{ color: 'var(--accent)' }}>✨ Fitment Score (RAG)</span>
                          ) : (
                            MODE_LABELS[scoringMode]
                          )}
                        </div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--primary)', lineHeight: 1 }}>
                          {scoringMode === 'fitment_mode' && p.ranking.fitment_score !== undefined
                            ? p.ranking.fitment_score
                            : scoringMode === 'dsa_mode' ? p.ranking.overall_dsa_mode
                            : scoringMode === 'github_mode' ? p.ranking.overall_github_mode
                            : p.ranking.custom_score ?? p.ranking.total_technical_score}
                          <span style={{ fontSize: '0.85rem', opacity: 0.6, fontWeight: 400 }}>/100</span>
                        </div>
                        <div className="score-mini" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'flex-end', marginTop: '0.25rem' }}>
                          {(p.ranking.lc_score ?? 0) > 0 && <span>LC: {p.ranking.lc_score}</span>}
                          {(p.ranking.cc_score ?? 0) > 0 && <span>CC: {p.ranking.cc_score}</span>}
                          {(p.ranking.cf_score ?? 0) > 0 && <span>CF: {p.ranking.cf_score}</span>}
                          {(p.ranking.github_score_total ?? 0) > 0 && <span>GH: {p.ranking.github_score_total}</span>}
                          {p.ranking.semantic_score !== undefined && p.ranking.semantic_score > 0 && (localStorage.getItem('active_jd') || scoringMode === 'fitment_mode') && (
                            <span style={{ color: 'var(--accent)', fontWeight: 700, background: 'rgba(0, 240, 255, 0.1)', padding: '0 0.25rem', borderRadius: '4px' }}>
                              SEM: {p.ranking.semantic_score}
                            </span>
                          )}
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

      {showExportPreview && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          backdropFilter: 'blur(4px)'
        }}>
          <div style={{
            background: 'var(--bg)',
            border: '1px solid var(--border)',
            borderRadius: '16px',
            width: '90%',
            maxWidth: '600px',
            maxHeight: '80vh',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 'var(--shadow-lg)'
          }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>Export Preview</h2>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>{exportPreviewData.length} records</span>
            </div>
            <div style={{ padding: '1rem 1.5rem', overflowY: 'auto', flex: 1 }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border)', textAlign: 'left' }}>
                    <th style={{ padding: '0.75rem 0.5rem', color: '#111827', fontWeight: 800 }}>Student Name</th>
                    <th style={{ padding: '0.75rem 0.5rem', color: '#111827', fontWeight: 800 }}>ID Number</th>
                    <th style={{ padding: '0.75rem 0.5rem', color: '#111827', fontWeight: 800 }}>Missing Platforms</th>
                  </tr>
                </thead>
                <tbody>
                  {exportPreviewData.slice(0, 10).map((row, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '0.75rem 0.5rem', color: '#111827', fontWeight: 600 }}>{row['Student Name']}</td>
                      <td style={{ padding: '0.75rem 0.5rem', color: '#111827', fontWeight: 600 }}>{row['ID Number']}</td>
                      <td style={{ padding: '0.75rem 0.5rem', fontWeight: 800, color: row['Missing Platforms'] === 'None' ? '#10b981' : '#ef4444' }}>
                        {row['Missing Platforms']}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {exportPreviewData.length > 10 && (
                <div style={{ textAlign: 'center', padding: '1rem', color: 'var(--text-tertiary)', fontSize: '0.8rem', fontStyle: 'italic' }}>
                  ... and {exportPreviewData.length - 10} more records
                </div>
              )}
            </div>
            <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '1rem', justifyContent: 'flex-end', background: 'var(--bg-secondary)', borderRadius: '0 0 16px 16px' }}>
              <button className="btn btn-ghost" onClick={() => setShowExportPreview(false)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleConfirmExport} style={{ backgroundColor: '#10b981', borderColor: '#10b981' }}>
                Download Excel ({exportPreviewData.length})
              </button>
            </div>
          </div>
        </div>
      )}

      {showResumeModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          backdropFilter: 'blur(4px)'
        }}>
          <div style={{
            background: 'var(--bg)',
            border: '1px solid var(--border)',
            borderRadius: '16px',
            width: '90%',
            maxWidth: '500px',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 'var(--shadow-lg)',
            overflow: 'hidden'
          }}>
            <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', backgroundColor: 'var(--surface)' }}>
              <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>Extraction Options</h2>
            </div>
            <div style={{ padding: '1.5rem', fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                <p style={{ margin: '0 0 1rem 0' }}>How would you like to proceed with the data extraction?</p>
                <ul style={{ paddingLeft: '1.5rem', marginBottom: 0 }}>
                  <li style={{ marginBottom: '0.5rem' }}><strong>Resume Extraction:</strong> Resumes from the old pausing area (syncs the remaining un-synced students).</li>
                  <li><strong>Sync All:</strong> Syncs all the students from the first and updates the database of the last sync for error handling and resuming purpose again.</li>
                </ul>
            </div>
            <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '1rem', justifyContent: 'flex-end', background: 'var(--bg-secondary)' }}>
              <button className="btn btn-ghost" onClick={() => setShowResumeModal(false)}>
                Cancel
              </button>
              
              <button 
                className="btn btn-primary" 
                onClick={() => startEnrich(true)}
                style={{ backgroundColor: '#ef4444', borderColor: '#ef4444', fontWeight: 700 }}
              >
                Sync All
              </button>

              <button 
                className="btn btn-primary" 
                onClick={() => startEnrich(false)}
                style={{ 
                  background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)', 
                  border: 'none',
                  fontWeight: 700 
                }}
              >
                Resume Extraction
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
