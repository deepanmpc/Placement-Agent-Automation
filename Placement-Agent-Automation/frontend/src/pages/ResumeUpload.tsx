import { useRef, useState } from 'react';

export default function ResumeUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
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

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
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
        <h1>Upload Resume</h1>
        <p className="page-subtitle">
          Upload a PDF, DOCX, or TXT file to parse structured candidate data
        </p>
      </div>

      <div className="upload-card">
        <div className="upload-zone" onClick={() => inputRef.current?.click()}>
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
              <span className="upload-file-size">
                {(file.size / 1024).toFixed(1)} KB
              </span>
            </div>
          ) : (
            <p className="upload-placeholder">
              Click to choose a file
            </p>
          )}
        </div>
        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!file || loading}
        >
          {loading ? 'Parsing...' : 'Upload and Parse'}
        </button>
        {error && <p className="upload-error">{error}</p>}
      </div>

      {result && (
        <div className="upload-result">
          <h3>Extracted Data</h3>
          <pre className="upload-json">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
