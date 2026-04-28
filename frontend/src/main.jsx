import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './theme-color.css'
import './index.css'
import App from './App.jsx'
import { ColorModeProvider } from './context/ColorModeContext.jsx'

const baseUrl = import.meta.env.BASE_URL || '/'
const routerBasename = baseUrl === '/' ? undefined : baseUrl.replace(/\/$/, '')

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ColorModeProvider>
      <BrowserRouter basename={routerBasename}>
        <App />
      </BrowserRouter>
    </ColorModeProvider>
  </StrictMode>,
)
