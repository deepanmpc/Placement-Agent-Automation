import sys

with open('frontend/src/pages/StudentDetail.tsx', 'r') as f:
    content = f.read()

old_semantic = """
                                {Object.entries(r.semantic_breakdown).map(([key, data]: [string, any], idx) => (
                                  <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                                    <td style={{ padding: '0.5rem', fontWeight: 600, textTransform: 'capitalize' }}>{key.replace('_', ' ')}</td>
                                    <td style={{ padding: '0.5rem', color: 'var(--text-primary)', maxWidth: '400px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{data.text_snippet}</td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 800, color: data.similarity_score > 70 ? '#10b981' : data.similarity_score > 40 ? '#f59e0b' : '#ef4444' }}>
                                      {data.similarity_score}%
                                    </td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', color: 'var(--text-muted)' }}>{data.weight}x</td>
                                  </tr>
                                ))}
"""

new_semantic = """
                                {Object.entries(r.semantic_breakdown.breakdown || {}).map(([key, value]: [string, any], idx) => (
                                  <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                                    <td style={{ padding: '0.5rem', fontWeight: 600, textTransform: 'capitalize' }}>{key.replace('_', ' ')}</td>
                                    <td style={{ padding: '0.5rem', color: 'var(--text-primary)', maxWidth: '400px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>-</td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 800, color: value > 70 ? '#10b981' : value > 40 ? '#f59e0b' : '#ef4444' }}>
                                      {value}
                                    </td>
                                    <td style={{ padding: '0.5rem', textAlign: 'right', color: 'var(--text-muted)' }}>-</td>
                                  </tr>
                                ))}
"""

if old_semantic.strip() in content:
    content = content.replace(old_semantic, new_semantic)
    with open('frontend/src/pages/StudentDetail.tsx', 'w') as f:
        f.write(content)
    print("Semantic table patched")
else:
    print("Semantic table not found or already patched")

