import { useEffect } from 'react'
import { useStage } from './context/useStage'
import Landing from './components/Landing/Landing'
import Boot from './components/Boot/Boot'
import HUD from './components/HUD/HUD'
import Intro from './components/Intro/Intro'
import Skills from './components/Skills/Skills'
import Projects from './components/Projects/Projects'
import Achievements from './components/Achievements/Achievements'
import ProjectModal from './components/ProjectModal/ProjectModal'
import Terminal from './components/Terminal/Terminal'
import Contact from './components/Contact/Contact'
import ChatBot from './components/ChatBot/ChatBot'

function App() {
  const { currentStage, modalProject, isTerminalOpen, isChatOpen, closeModal, closeTerminal, closeChat, toggleTerminal, openChat, isAnyOverlayOpen } = useStage()

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null
      const isEditable = target?.tagName === 'INPUT' || target?.tagName === 'TEXTAREA' || target?.isContentEditable

      if (e.key === 'Escape') {
        if (modalProject) {
          e.preventDefault()
          closeModal()
        } else if (isTerminalOpen) {
          e.preventDefault()
          closeTerminal()
        } else if (isChatOpen) {
          e.preventDefault()
          closeChat()
        }
        return
      }

      if (!isAnyOverlayOpen && e.key === '~') {
        e.preventDefault()
        toggleTerminal()
        return
      }

      if (!isAnyOverlayOpen && e.key.toLowerCase() === 'c' && !isEditable) {
        e.preventDefault()
        openChat()
        return
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [modalProject, isTerminalOpen, isChatOpen, closeModal, closeTerminal, closeChat, toggleTerminal, openChat, isAnyOverlayOpen])

  const renderStage = () => {
    switch (currentStage) {
      case 'landing':
        return <Landing />
      case 'boot':
        return <Boot />
      case 'hud':
        return null
      case 'intro':
        return <Intro />
      case 'skills':
        return <Skills />
      case 'projects':
        return <Projects />
      case 'achievements':
        return <Achievements />
      case 'contact':
        return <Contact />
      default:
        return <Landing />
    }
  }

  return (
    <>
      <div className="grid-overlay" />
      <div className="noise-overlay" />
      <div className={`${isAnyOverlayOpen ? 'dimmed-focus' : ''} stage-wrapper`}>
        <HUD />
        {renderStage()}
      </div>
      <ProjectModal />
      <Terminal />
      <ChatBot />
    </>
  )
}

export default App