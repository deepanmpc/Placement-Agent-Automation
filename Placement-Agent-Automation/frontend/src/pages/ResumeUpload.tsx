import { useRef, useState } from 'react';

export default function ResumeUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [idNumber, setIdNumber] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const [codeforcesUsername, setCodeforcesUsername] = useState('');
  const [codechefUsername, setCodechefUsername] = useState('');

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setFile(f);
    setError(null);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    if (idNumber) formData.append('id_number', idNumber);
    if (githubUrl) formData.append('github_url', githubUrl);
    if (linkedinUrl) formData.append('linkedin_url', linkedinUrl);
    if (leetcodeUsername) formData.append('leetcode_username', leetcodeUsername);
    if (codeforcesUsername) formData.append('codeforces_username', codeforcesUsername);
    if (codechefUsername) formData.append('codechef_username', codechefUsername);

    try {
      const response = await fetch('http://localhost:8000/ingest', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error("This candidate's data is already registered in the system!");
        }
        const errorText = await response.text();
        try {
          const errObj = JSON.parse(errorText);
          throw new Error(`${errObj.detail || response.statusText}`);
        } catch {
          throw new Error(`Upload Failed: ${response.statusText}`);
        }
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Add Candidate Profile</h1>
        <p className="page-subtitle">
          Upload a resume and manually provide platform usernames (optional).
        </p>
      </div>

      <div className="upload-card">
        <div className="upload-zone" onClick={() => inputRef.current?.click()} style={{ padding: '2rem' }}>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            onChange={handleFileChange}
            className="upload-input"
          />
          {file ? (
            <div className="upload-file-info">
              <span className="upload-file-name">{file.name}</span>
            </div>
          ) : (
            <p className="upload-placeholder">
              Click to choose resume file
            </p>
          )}
        </div>

        <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem', color: '#94a3b8' }}>ID Number / Roll Number</label>
            <input type="text" className="form-input" value={idNumber} onChange={e => setIdNumber(e.target.value)} placeholder="e.g. 21BCE001" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc' }} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem', color: '#94a3b8' }}>GitHub Profile URL</label>
            <input type="text" className="form-input" value={githubUrl} onChange={e => setGithubUrl(e.target.value)} placeholder="https://github.com/username" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc' }} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem', color: '#94a3b8' }}>LinkedIn URL</label>
            <input type="text" className="form-input" value={linkedinUrl} onChange={e => setLinkedinUrl(e.target.value)} placeholder="https://linkedin.com/in/username" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc' }} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem', color: '#94a3b8' }}>LeetCode Username</label>
            <input type="text" className="form-input" value={leetcodeUsername} onChange={e => setLeetcodeUsername(e.target.value)} placeholder="e.g. jdoe123" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc' }} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem', color: '#94a3b8' }}>Codeforces Handle</label>
            <input type="text" className="form-input" value={codeforcesUsername} onChange={e => setCodeforcesUsername(e.target.value)} placeholder="e.g. tourist" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc' }} />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem', color: '#94a3b8' }}>CodeChef Username</label>
            <input type="text" className="form-input" value={codechefUsername} onChange={e => setCodechefUsername(e.target.value)} placeholder="e.g. coder_123" style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #334155', backgroundColor: '#0f172a', color: '#f8fafc' }} />
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!file || loading}
          style={{ marginTop: '1.5rem', width: '100%' }}
        >
          {loading ? 'Creating Profile...' : 'Upload & Create Candidate Profile'}
        </button>
        {error && (
          <div className="upload-error" style={{ textAlign: 'left', marginTop: '1rem' }}>
            <p><strong>Error:</strong> {error}</p>
          </div>
        )}
      </div>

      {result && (
        <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '2rem', animation: 'fadeIn 0.5s ease' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: '#10b981',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
            boxShadow: '0 0 20px rgba(16, 185, 129, 0.4)'
          }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
          <h3 style={{ margin: 0, color: '#f8fafc', fontSize: '1.25rem', fontWeight: 600 }}>Upload Successful</h3>
          <p style={{ color: '#94a3b8', marginTop: '0.5rem', textAlign: 'center' }}>
            {result.personal_info?.name || 'Candidate'} added to dashboard.
          </p>
          <button 
            onClick={() => { setResult(null); setFile(null); setIdNumber(''); setGithubUrl(''); setLinkedinUrl(''); setLeetcodeUsername(''); setCodeforcesUsername(''); setCodechefUsername(''); }}
            className="btn"
            style={{ marginTop: '1.5rem', backgroundColor: '#1e293b', border: '1px solid #334155' }}
          >
            Upload Another
          </button>
        </div>
      )}
    </div>
  );
}
