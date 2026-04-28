import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './styles/global.css'
import { StageProvider } from './context/StageProvider'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <StageProvider>
      <App />
    </StageProvider>
  </React.StrictMode>,
)
