import sys

with open('frontend/src/pages/EditProfile.tsx', 'r') as f:
    content = f.read()

# Add a section to upload resume
resume_section = """
                <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border)' }}>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>Re-upload Resume (Optional)</h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
                    Upload a new resume to update the student's extracted skills, projects, and education. Existing platform links will be preserved.
                  </p>
                  <input type="file" accept=".pdf,.docx,.txt,.md" onChange={(e) => setResumeFile(e.target.files?.[0] || null)} style={inputStyle} />
                </div>
"""

# Replace the closing form div area
if "setResumeFile" not in content:
    # 1. Add state variable
    content = content.replace("const [codechef, setCodechef] = useState('');", "const [codechef, setCodechef] = useState('');\n  const [resumeFile, setResumeFile] = useState<File | null>(null);")
    
    # 2. Add resume API call logic to handleUpdate
    update_logic = """
      const res = await fetch(`http://localhost:8000/profiles/${studentUuid}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) throw new Error('Failed to update profile');
      
      if (resumeFile) {
        const formData = new FormData();
        formData.append('file', resumeFile);
        const resumeRes = await fetch(`http://localhost:8000/profiles/${studentUuid}/resume`, {
          method: 'POST',
          body: formData
        });
        if (!resumeRes.ok) throw new Error('Failed to update resume');
      }
"""
    
    old_update_logic = """
      const res = await fetch(`http://localhost:8000/profiles/${studentUuid}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) throw new Error('Failed to update profile');
"""
    content = content.replace(old_update_logic, update_logic)
    
    # 3. Add UI element
    target_ui = """                <label style={labelStyle}>CodeChef Username</label>
                <input type="text" value={codechef} onChange={e => setCodechef(e.target.value)} style={inputStyle} />
              </div>"""
    
    content = content.replace(target_ui, target_ui + resume_section)
    
    with open('frontend/src/pages/EditProfile.tsx', 'w') as f:
        f.write(content)
    print("EditProfile.tsx patched")
else:
    print("EditProfile.tsx already patched")
