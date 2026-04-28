/* eslint-disable react-refresh/only-export-components -- provider e hook no mesmo arquivo */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

const STORAGE_KEY = 'equivoz_color_mode'

const ColorModeContext = createContext({
  mode: 'padrao',
  isDaltonismo: false,
  setMode: () => {},
  toggleDaltonismo: () => {},
})

function applyToDocument(mode) {
  const root = document.documentElement
  if (mode === 'daltonismo') {
    root.setAttribute('data-color-mode', 'daltonismo')
  } else {
    root.removeAttribute('data-color-mode')
  }
  try {
    localStorage.setItem(STORAGE_KEY, mode)
  } catch {
    /* storage indisponível */
  }
}

export function ColorModeProvider({ children }) {
  const [mode, setModeState] = useState(() => {
    if (typeof window === 'undefined') return 'padrao'
    try {
      return localStorage.getItem(STORAGE_KEY) === 'daltonismo' ? 'daltonismo' : 'padrao'
    } catch {
      return 'padrao'
    }
  })

  useEffect(() => {
    applyToDocument(mode)
  }, [mode])

  const setMode = useCallback((m) => {
    setModeState(m === 'daltonismo' ? 'daltonismo' : 'padrao')
  }, [])

  const toggleDaltonismo = useCallback(() => {
    setModeState((prev) => (prev === 'daltonismo' ? 'padrao' : 'daltonismo'))
  }, [])

  const isDaltonismo = mode === 'daltonismo'

  const value = useMemo(
    () => ({ mode, isDaltonismo, setMode, toggleDaltonismo }),
    [mode, isDaltonismo, setMode, toggleDaltonismo],
  )

  return <ColorModeContext.Provider value={value}>{children}</ColorModeContext.Provider>
}

export function useColorMode() {
  return useContext(ColorModeContext)
}
