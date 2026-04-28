import { useStage } from './context/useStage'
import Landing from './components/Landing/Landing'
import Boot from './components/Boot/Boot'
import HUD from './components/HUD/HUD'
import Intro from './components/Intro/Intro'
import Skills from './components/Skills/Skills'
import Projects from './components/Projects/Projects'
import ProjectModal from './components/ProjectModal/ProjectModal'

function App() {
  const { currentStage, modalProject } = useStage()

  const renderStage = () => {
    switch (currentStage) {
      case 'landing':
        return <Landing />
      case 'boot':
        return <Boot />
      case 'hud':
        return null // HUD handles its own reveal animation
      case 'intro':
        return <Intro />
      case 'skills':
        return <Skills />
      case 'projects':
        return <Projects />
      case 'contact':
        return <div style={{ padding: '80px', color: '#00e5c0', fontSize: '24px' }} className="syne">STAGE 9: CONTACT LOADING...</div>
      default:
        return <Landing />
    }
  }

  return (
    <>
      <div className="grid-overlay" />
      <div className="noise-overlay" />
      <div className={`${modalProject ? 'dimmed-focus' : ''} stage-wrapper`}>
        <HUD />
        {renderStage()}
      </div>
      <ProjectModal />
    </>
  )
}

export default App
