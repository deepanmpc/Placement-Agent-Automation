import React, { useState, useEffect } from 'react';

export default function EditProfile() {
  const [step, setStep] = useState<1 | 2>(1);
  const [searchId, setSearchId] = useState('');
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [profiles, setProfiles] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
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

  useEffect(() => {
    fetch('http://localhost:8000/profiles', { cache: 'no-store' })
      .then(res => res.json())
      .then(data => {
        setProfiles(data);
        setIsLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('Failed to load profiles');
        setIsLoading(false);
      });
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    
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
    setSuccessMsg('');
    
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
      
      setSuccessMsg('Profile updated successfully!');
      setTimeout(() => {
        setStep(1);
        setSearchId('');
        setSuccessMsg('');
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
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

  if (isLoading) {
    return <div className="page"><div className="page-header"><h1>Loading...</h1></div></div>;
  }

  return (
    <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80vh' }}>
      <div style={{ background: 'var(--card-bg)', borderRadius: '16px', width: '100%', maxWidth: '500px', boxShadow: 'var(--shadow-lg)', overflow: 'hidden', border: '1px solid var(--border)' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border)' }}>
          <h2 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--text-primary)' }}>Edit Student Profile</h2>
        </div>
        
        <div style={{ padding: '1.5rem' }}>
          {error && <div style={{ padding: '0.75rem', background: 'var(--color-danger-bg)', color: 'var(--color-danger)', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem' }}>{error}</div>}
          {successMsg && <div style={{ padding: '0.75rem', background: 'var(--color-success-bg)', color: 'var(--color-success)', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem' }}>{successMsg}</div>}
          
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
                <button type="button" onClick={() => { setStep(1); setSuccessMsg(''); }} disabled={isSubmitting} style={{ padding: '0.75rem 1.25rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-secondary)', color: 'var(--text-primary)', cursor: 'pointer', fontWeight: 600 }}>Back</button>
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
