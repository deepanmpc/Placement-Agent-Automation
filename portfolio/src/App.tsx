import { useStage } from './context/useStage'
import Landing from './components/Landing/Landing'
import Boot from './components/Boot/Boot'
import HUD from './components/HUD/HUD'
import Intro from './components/Intro/Intro'

function App() {
  const { currentStage } = useStage()

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
      default:
        return <Landing />
    }
  }

  return (
    <>
      <div className="grid-overlay" />
      <div className="noise-overlay" />
      <HUD />
      {renderStage()}
    </>
  )
}

export default App
