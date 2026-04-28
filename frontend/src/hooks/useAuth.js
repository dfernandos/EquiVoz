import { useCallback, useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { EQUIVOZ_AUTH_EVENT, getToken } from '../api/client'

/**
 * Sincroniza estado de login com o token (mesma aba) e com outras abas (storage).
 */
export function useAuth() {
  const location = useLocation()
  const [loggedIn, setLoggedIn] = useState(() => Boolean(getToken()))

  const sync = useCallback(() => {
    setLoggedIn(Boolean(getToken()))
  }, [])

  useEffect(() => {
    const id = requestAnimationFrame(() => sync())
    return () => cancelAnimationFrame(id)
  }, [location.pathname, sync])

  useEffect(() => {
    const on = () => sync()
    window.addEventListener(EQUIVOZ_AUTH_EVENT, on)
    window.addEventListener('storage', on)
    return () => {
      window.removeEventListener(EQUIVOZ_AUTH_EVENT, on)
      window.removeEventListener('storage', on)
    }
  }, [sync])

  return loggedIn
}
