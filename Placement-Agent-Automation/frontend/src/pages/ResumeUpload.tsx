import { useRef, useState } from 'react';

export default function ResumeUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [errors, setErrors] = useState<string[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = Array.from(e.target.files || []);
    setFiles(f);
    setErrors([]);
    setResults([]);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setLoading(true);
    setErrors([]);
    setResults([]);

    const newResults: any[] = [];
    const newErrors: string[] = [];

    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch('http://localhost:8000/ingest', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          try {
            const errObj = JSON.parse(errorText);
            throw new Error(`${file.name}: ${errObj.detail || response.statusText}`);
          } catch {
            throw new Error(`${file.name}: ${response.statusText}`);
          }
        }

        const data = await response.json();
        newResults.push(data);
      } catch (err: any) {
        newErrors.push(err.message);
      }
    }

    setResults(newResults);
    setErrors(newErrors);
    setLoading(false);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Upload Resumes</h1>
        <p className="page-subtitle">
          Upload PDF, DOCX, or TXT files to parse structured candidate data
        </p>
      </div>

      <div className="upload-card">
        <div className="upload-zone" onClick={() => inputRef.current?.click()}>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            multiple
            onChange={handleFileChange}
            className="upload-input"
          />
          {files.length > 0 ? (
            <div className="upload-file-info">
              <span className="upload-file-name">{files.length} file(s) selected</span>
              <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#94a3b8' }}>
                {files.slice(0, 3).map(f => f.name).join(', ')}
                {files.length > 3 && ` and ${files.length - 3} more`}
              </div>
            </div>
          ) : (
            <p className="upload-placeholder">
              Click to choose files (multiple allowed)
            </p>
          )}
        </div>
        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={files.length === 0 || loading}
        >
          {loading ? 'Parsing...' : `Upload and Parse ${files.length > 0 ? files.length : ''}`}
        </button>
        {errors.length > 0 && (
          <div className="upload-error" style={{ textAlign: 'left', marginTop: '1rem' }}>
            <p><strong>Errors:</strong></p>
            <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
              {errors.map((e, idx) => <li key={idx}>{e}</li>)}
            </ul>
          </div>
        )}
      </div>

      {results.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Successfully Extracted ({results.length})</h3>
          <div style={{ display: 'grid', gap: '1rem', marginTop: '1rem' }}>
            {results.map((result, idx) => (
              <div key={idx} className="upload-result" style={{ padding: '1.5rem', backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155' }}>
                <h4 style={{ marginBottom: '1rem', color: '#f8fafc', fontSize: '1.1rem', margin: '0 0 1rem 0' }}>
                  <span style={{ color: '#38bdf8' }}>{result.personal_info?.name || 'Unknown Candidate'}</span>
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', color: '#cbd5e1', fontSize: '0.9rem' }}>
                  <div>
                    <p style={{ margin: '0 0 0.25rem 0' }}><strong style={{ color: '#94a3b8' }}>College:</strong> {result.education?.college || 'N/A'}</p>
                    <p style={{ margin: '0 0 0.25rem 0' }}><strong style={{ color: '#94a3b8' }}>Email:</strong> {result.personal_info?.email || 'N/A'}</p>
                  </div>
                  <div>
                    <p style={{ margin: '0 0 0.25rem 0' }}><strong style={{ color: '#94a3b8' }}>GitHub:</strong> {result.personal_info?.github_url || 'N/A'}</p>
                    <p style={{ margin: '0 0 0.25rem 0' }}><strong style={{ color: '#94a3b8' }}>LeetCode:</strong> {result.personal_info?.leetcode_username || 'N/A'}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#0f172a', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
            <p style={{ color: '#10b981', margin: 0, fontWeight: 500 }}>
              Profiles saved! Go to the Candidates Dashboard and click "Extract Coding & GitHub Data" to enrich them.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
