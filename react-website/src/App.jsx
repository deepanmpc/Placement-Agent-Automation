import { useState, useEffect } from 'react'
import { Sun, Moon, Play, ArrowRight, Terminal, Eye, Brain, Zap, ShieldCheck, Activity, Cpu, MessageSquare } from 'lucide-react'
import './index.css'

function App() {
  const [theme, setTheme] = useState('light')
  const [activeModel, setActiveModel] = useState(0)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  // Animation loop for the multi-model section
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveModel((prev) => (prev + 1) % 4)
    }, 2500)
    return () => clearInterval(interval)
  }, [])

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText('git clone https://github.com/deepanmpc/COWORK_AGENT_DESKTOP_AUTOMATION')
  }

  return (
    <div className="min-h-screen">
      <div className="glow-bg"></div>
      
      <nav className="navbar">
        <div className="nav-content">
          <div className="logo">
            <div className="logo-cube"></div>
            <span className="logo-text">COWORK</span>
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#multi-model">Reasoning Loop</a>
            <button onClick={toggleTheme} className="theme-toggle" aria-label="Toggle Theme">
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <a href="https://github.com/deepanmpc/COWORK_AGENT_DESKTOP_AUTOMATION" target="_blank" rel="noreferrer" className="btn btn-github">
              Star on GitHub
            </a>
          </div>
        </div>
      </nav>

      <main>
        <section className="hero">
          <div className="hero-container">
            <div className="hero-badge">
              <span className="pulse-dot"></span>
              E.D.I.T.H. v2.0 is live
            </div>
            <h1 className="hero-title">
              The autonomous <br />
              <span className="gradient-text">desktop agent</span> for macOS.
            </h1>
            <p className="hero-subtitle">
              Give it a goal. It sees your screen, reasons, and acts — like a human co-worker who never sleeps.
            </p>
            
            <div className="hero-ctas">
              <a href="#demo" className="btn btn-primary">
                Watch Demo <Play size={18} />
              </a>
              <button onClick={copyToClipboard} className="btn btn-secondary">
                <Terminal size={18} /> git clone cowork
              </button>
            </div>
          </div>

          <div id="demo" className="hero-visual-wrapper">
            <div className="app-window">
              <div className="window-header">
                <div className="window-controls">
                  <span className="control red"></span>
                  <span className="control yellow"></span>
                  <span className="control green"></span>
                </div>
                <div className="window-title">Global CLI Trigger (edith)</div>
              </div>
              <div className="window-body video-container">
                <video src="/demo.mov" autoPlay loop muted playsInline className="demo-video" />
              </div>
            </div>
          </div>
        </section>

        {/* Multi-Model Reasoning Loop Section */}
        <section id="multi-model" className="multi-model-section">
          <div className="section-header">
            <h2>Multi-Model Orchestration</h2>
            <p>Watch how 4 state-of-the-art models communicate in a continuous loop to solve complex tasks autonomously.</p>
          </div>

          <div className="orchestration-container">
            <div className="network-flow">
              {/* Llama Vision Node */}
              <div className={`model-node ${activeModel === 0 ? 'active' : ''}`}>
                <div className="node-icon"><Eye size={24} /></div>
                <h4>Llama Vision</h4>
                <div className="node-log">
                  {activeModel === 0 ? "> Processing screen pixels. Identifying shapes and layout..." : "Waiting..."}
                </div>
              </div>

              {/* Arrow */}
              <div className={`flow-arrow ${activeModel === 0 ? 'active-arrow' : ''}`}>
                <ArrowRight size={24} />
              </div>

              {/* OmniParser Node */}
              <div className={`model-node ${activeModel === 1 ? 'active' : ''}`}>
                <div className="node-icon"><Activity size={24} /></div>
                <h4>OmniParser</h4>
                <div className="node-log">
                  {activeModel === 1 ? "> Extracting interactable elements. Built UI DOM with 34 nodes." : "Waiting..."}
                </div>
              </div>

              {/* Arrow */}
              <div className={`flow-arrow ${activeModel === 1 ? 'active-arrow' : ''}`}>
                <ArrowRight size={24} />
              </div>

              {/* Opus 4.6 Node */}
              <div className={`model-node ${activeModel === 2 ? 'active opus' : ''}`}>
                <div className="node-icon"><Brain size={24} /></div>
                <h4>Claude Opus 4.6</h4>
                <div className="node-log">
                  {activeModel === 2 ? "> Reasoning: The user wants to login. I must click node [12] 'Username', type text, then click node [15] 'Submit'." : "Waiting..."}
                </div>
              </div>

              {/* Arrow */}
              <div className={`flow-arrow ${activeModel === 2 ? 'active-arrow' : ''}`}>
                <ArrowRight size={24} />
              </div>

              {/* GPT-OSS Node */}
              <div className={`model-node ${activeModel === 3 ? 'active' : ''}`}>
                <div className="node-icon"><MessageSquare size={24} /></div>
                <h4>GPT-OSS (Chat)</h4>
                <div className="node-log">
                  {activeModel === 3 ? "> Orchestrating execution... Dispatching OS clicks. Loop complete." : "Waiting..."}
                </div>
              </div>
            </div>
            
            {/* Loop Back Arrow (visual representation) */}
            <div className={`loop-back ${activeModel === 3 ? 'active-loop' : ''}`}>
                <div className="loop-line"></div>
                <span>Verify State & Loop</span>
            </div>
          </div>
        </section>

        <section id="features" className="features-section">
          <div className="section-header">
            <h2>Core Features.</h2>
            <p>Four powerful services working in harmony to operate your macOS environment.</p>
          </div>

          <div className="bento-grid">
            <div className="bento-card large">
              <div className="card-icon"><Eye size={24} /></div>
              <h3>Computer Vision</h3>
              <p>Captures your screen in milliseconds using MSS. Passes the frame through PaddleOCR and OmniParser to build a token-compressed JSON graph of your UI elements.</p>
              <div className="visual-placeholder vision-bg"></div>
            </div>

            <div className="bento-card">
              <div className="card-icon"><Brain size={24} /></div>
              <h3>Multi-step Planning</h3>
              <p>Powered by NVIDIA NIM (Llama 3.3 / GPT-OSS). It reasons about the goal, analyzes the UI state, and generates batched action queues.</p>
            </div>

            <div className="bento-card">
              <div className="card-icon"><Zap size={24} /></div>
              <h3>Native Execution</h3>
              <p>Translates logical actions into real macOS events (clicks, typing, shortcuts) natively via PyAutoGUI and PyObjC.</p>
            </div>

            <div className="bento-card wide">
              <div className="card-icon"><ShieldCheck size={24} /></div>
              <h3>Self-Healing Verification</h3>
              <p>After execution, the Verifier Service takes a new screenshot. It compares the before/after state to detect loops, verify progress, and automatically recover from errors.</p>
            </div>
          </div>
        </section>
      </main>
      
      <footer>
        <div className="footer-content">
            <div className="logo">
                <div className="logo-cube"></div>
                <span className="logo-text">COWORK</span>
            </div>
            <p>MIT Licensed. Built by deepanmpc.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
