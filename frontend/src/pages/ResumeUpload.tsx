import { useRef, useState } from 'react';

export default function ResumeUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [idNumber, setIdNumber] = useState('');
  const [batch, setBatch] = useState('2026');
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
    if (batch) formData.append('graduation_year', batch);
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

      <div className="upload-card" style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
        <div className="upload-zone" onClick={() => inputRef.current?.click()} style={{ padding: '3rem 2rem', marginBottom: '2rem', borderStyle: 'dashed' }}>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            onChange={handleFileChange}
            className="upload-input"
          />
          {file ? (
            <div className="upload-file-info">
              <span className="upload-file-name" style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--accent)' }}>{file.name}</span>
            </div>
          ) : (
            <p className="upload-placeholder" style={{ fontSize: '1.05rem' }}>
              Click or drag to choose resume file
            </p>
          )}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="form-group">
            <label className="form-label">ID Number / Roll Number</label>
            <input type="text" className="form-input" value={idNumber} onChange={e => setIdNumber(e.target.value)} placeholder="23000*****" />
          </div>
          <div className="form-group">
            <label className="form-label">Graduation Batch</label>
            <select 
              className="form-input" 
              value={batch} 
              onChange={e => setBatch(e.target.value)}
              style={{ cursor: 'pointer' }}
            >
              <option value="2023">Y23</option>
              <option value="2024">Y24</option>
              <option value="2025">Y25</option>
              <option value="2026">Y26</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">GitHub Profile URL</label>
            <input type="text" className="form-input" value={githubUrl} onChange={e => setGithubUrl(e.target.value)} placeholder="https://github.com/username" />
          </div>
          <div className="form-group">
            <label className="form-label">LinkedIn URL</label>
            <input type="text" className="form-input" value={linkedinUrl} onChange={e => setLinkedinUrl(e.target.value)} placeholder="https://linkedin.com/in/username" />
          </div>
          <div className="form-group">
            <label className="form-label">LeetCode Username</label>
            <input type="text" className="form-input" value={leetcodeUsername} onChange={e => setLeetcodeUsername(e.target.value)} placeholder="klu23000*****" />
          </div>
          <div className="form-group">
            <label className="form-label">Codeforces Handle</label>
            <input type="text" className="form-input" value={codeforcesUsername} onChange={e => setCodeforcesUsername(e.target.value)} placeholder="klu23000*****" />
          </div>
          <div className="form-group" style={{ gridColumn: 'span 2' }}>
            <label className="form-label">CodeChef Username</label>
            <input type="text" className="form-input" value={codechefUsername} onChange={e => setCodechefUsername(e.target.value)} placeholder="klu23000*****" />
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!file || loading}
          style={{ width: '100%', padding: '1rem', fontSize: '1rem', fontWeight: 600 }}
        >
          {loading ? 'Creating Profile...' : 'Upload & Create Candidate Profile'}
        </button>
        
        {error && (
          <div className="upload-error" style={{ textAlign: 'left', marginTop: '1rem', padding: '1rem', backgroundColor: 'var(--color-danger-bg)', color: 'var(--color-danger)', borderRadius: '8px' }}>
            <strong>Error:</strong> {error}
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
          <h3 style={{ margin: 0, color: '#f8fafc', fontSize: '1.25rem', fontWeight: 600 }}>Registration Successful</h3>
          <p style={{ color: '#94a3b8', marginTop: '0.5rem', textAlign: 'center' }}>
            Your profile has been submitted and registered successfully.
          </p>
        </div>
      )}
    </div>
  );
}
