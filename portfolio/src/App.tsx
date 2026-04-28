import { useStage } from './context/useStage'
import Landing from './components/Landing/Landing'

function App() {
  const { currentStage } = useStage()

  const renderStage = () => {
    switch (currentStage) {
      case 'landing':
        return <Landing />
      case 'boot':
        return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#00e5c0' }}>STAGE 2: BOOT SEQUENCE</div>
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
