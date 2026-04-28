import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

const SYSTEM_PROMPT = `You are the system assistant for Deepan Chandrasekaran's portfolio.
- Short responses only (max 2-3 lines)
- No generic AI tone
- Answers only from portfolio data
- Direct, technical, confident
- No emojis, no fluff

Portfolio data:
- Skills: React, TypeScript, Python, PyTorch, RAG, FastAPI, FAISS, Docker, CV, LangChain, Vector DBs, AWS
- Projects: LaRa (real-time AI), SignSpeak AI (45 FPS), ResumeAnalyse (RAG), Search Wizard (50K+ files), AI Therapy System, 3D Apparel Customizer
- Education: B.Tech CSE, KL University, CGPA 9.15
- Certifications: Oracle Cloud GenAI Professional, Oracle AI Vector Search Professional
- Contact: 2300032731cse3@gmail.com | linkedin.com/in/deepanmpc/`;

app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;

    if (!message) {
      return res.status(400).json({ reply: 'Message required.' });
    }

    const apiKey = process.env.GEMINI_API_KEY;
    const prompt = `${SYSTEM_PROMPT}\n\nUser: ${message}`;

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ role: 'user', parts: [{ text: prompt }] }],
          generationConfig: {
            maxOutputTokens: 150,
            temperature: 0.7,
          },
        }),
      }
    );

    if (!response.ok) {
      console.error('Gemini API error:', await response.text());
      return res.json({ reply: 'System unavailable. Try again.' });
    }

    const data = await response.json();
    const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'No response.';

    res.json({ reply: reply.slice(0, 300) });
  } catch (err) {
    console.error('Chat error:', err);
    res.json({ reply: 'System error. Try again.' });
  }
});

app.listen(PORT, () => {
  console.log(`API running on port ${PORT}`);
});