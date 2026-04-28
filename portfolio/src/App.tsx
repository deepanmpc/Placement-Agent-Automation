import { useStage } from './context/useStage'
import Landing from './components/Landing/Landing'
import Boot from './components/Boot/Boot'

function App() {
  const { currentStage } = useStage()

  const renderStage = () => {
    switch (currentStage) {
      case 'landing':
        return <Landing />
      case 'boot':
        return <Boot />
      case 'intro':
        return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#00e5c0' }}>STAGE 3: INTRO SCENE</div>
      default:
        return <Landing />
    }
  }

  return (
    <>
      <div className="grid-overlay" />
      <div className="noise-overlay" />
      {renderStage()}
    </>
  )
}

export default App
