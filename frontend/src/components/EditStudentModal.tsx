import React, { useState } from 'react';

interface Props {
  onClose: () => void;
  onSuccess: () => void;
  profiles: any[];
}

export default function EditStudentModal({ onClose, onSuccess, profiles }: Props) {
  const [step, setStep] = useState<1 | 2>(1);
  const [searchId, setSearchId] = useState('');
  const [error, setError] = useState('');
  
  // Form fields
  const [studentUuid, setStudentUuid] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [idNumber, setIdNumber] = useState('');
  const [github, setGithub] = useState('');
  const [leetcode, setLeetcode] = useState('');
  const [codeforces, setCodeforces] = useState('');
  const [codechef, setCodechef] = useState('');
  
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Find student by ID Number (or fallback to UUID if they paste UUID)
    const found = profiles.find(p => 
      (p.personal_info?.id_number && p.personal_info.id_number.toLowerCase() === searchId.toLowerCase()) ||
      p.student_uuid === searchId
    );
    
    if (found) {
      setStudentUuid(found.student_uuid);
      setName(found.personal_info?.name || '');
      setEmail(found.personal_info?.email || '');
      setIdNumber(found.personal_info?.id_number || '');
      setGithub(found.personal_info?.github_url || '');
      setLeetcode(found.personal_info?.leetcode_username || '');
      setCodeforces(found.personal_info?.codeforces_username || '');
      setCodechef(found.personal_info?.codechef_username || '');
      setStep(2);
    } else {
      setError('Student not found with this ID Number.');
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    
    try {
      const payload = {
        name,
        email,
        id_number: idNumber,
        github_url: github,
        leetcode_username: leetcode,
        codeforces_username: codeforces,
        codechef_username: codechef
      };
      
      const res = await fetch(`http://localhost:8000/profiles/${studentUuid}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) throw new Error('Failed to update profile');
      
      onSuccess();
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      setIsSubmitting(false);
    }
  };

  const inputStyle = {
    width: '100%', padding: '0.75rem', borderRadius: '8px', 
    border: '1px solid var(--border)', background: 'var(--bg-primary)',
    color: 'var(--text-primary)', marginBottom: '1rem',
    fontFamily: 'inherit', fontSize: '0.9rem'
  };

  const labelStyle = {
    display: 'block', fontSize: '0.8rem', fontWeight: 600, 
    color: 'var(--text-secondary)', marginBottom: '0.35rem'
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
      <div style={{ background: 'var(--card-bg)', borderRadius: '16px', width: '100%', maxWidth: '500px', boxShadow: 'var(--shadow-lg)', overflow: 'hidden' }}>
        
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--text-primary)' }}>Edit Student Profile</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-tertiary)', cursor: 'pointer', fontSize: '1.5rem', lineHeight: 1 }}>&times;</button>
        </div>
        
        <div style={{ padding: '1.5rem' }}>
          {error && <div style={{ padding: '0.75rem', background: 'var(--color-danger-bg)', color: 'var(--color-danger)', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem' }}>{error}</div>}
          
          {step === 1 ? (
            <form onSubmit={handleSearch}>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
                Enter the student's ID Number (primary key) to search and map their profile for editing.
              </p>
              <label style={labelStyle}>ID Number</label>
              <input 
                type="text" 
                value={searchId} 
                onChange={e => setSearchId(e.target.value)} 
                placeholder="e.g. 21BQR001" 
                style={inputStyle} 
                required 
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" onClick={onClose} style={{ padding: '0.75rem 1.25rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', cursor: 'pointer', fontWeight: 600 }}>Cancel</button>
                <button type="submit" style={{ padding: '0.75rem 1.25rem', borderRadius: '8px', border: 'none', background: 'var(--accent)', color: '#fff', cursor: 'pointer', fontWeight: 600 }}>Search Student</button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleUpdate}>
              <div style={{ maxHeight: '50vh', overflowY: 'auto', paddingRight: '0.5rem' }}>
                <label style={labelStyle}>Full Name</label>
                <input type="text" value={name} onChange={e => setName(e.target.value)} style={inputStyle} />
                
                <label style={labelStyle}>ID Number</label>
                <input type="text" value={idNumber} onChange={e => setIdNumber(e.target.value)} style={inputStyle} />
                
                <label style={labelStyle}>Email</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} style={inputStyle} />
                
                <label style={labelStyle}>GitHub URL (or Username)</label>
                <input type="text" value={github} onChange={e => setGithub(e.target.value)} style={inputStyle} />
                
                <label style={labelStyle}>LeetCode Username</label>
                <input type="text" value={leetcode} onChange={e => setLeetcode(e.target.value)} style={inputStyle} />
                
                <label style={labelStyle}>Codeforces Username</label>
                <input type="text" value={codeforces} onChange={e => setCodeforces(e.target.value)} style={inputStyle} />
                
                <label style={labelStyle}>CodeChef Username</label>
                <input type="text" value={codechef} onChange={e => setCodechef(e.target.value)} style={inputStyle} />
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="button" onClick={() => setStep(1)} disabled={isSubmitting} style={{ padding: '0.75rem 1.25rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', cursor: 'pointer', fontWeight: 600 }}>Back</button>
                <button type="submit" disabled={isSubmitting} style={{ padding: '0.75rem 1.25rem', borderRadius: '8px', border: 'none', background: 'var(--accent)', color: '#fff', cursor: isSubmitting ? 'not-allowed' : 'pointer', fontWeight: 600, opacity: isSubmitting ? 0.7 : 1 }}>
                  {isSubmitting ? 'Saving...' : 'Update Profile'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
