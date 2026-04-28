import { startTransition, useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from './useAuth'

/**
 * Dados do usuário autenticado (a partir de /api/auth/me), ou null.
 */
export function useUser() {
  const loggedIn = useAuth()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!loggedIn) {
      return
    }
    let cancelled = false
    startTransition(() => {
      setUser(null)
      setLoading(true)
    })
    api('/api/auth/me')
      .then((d) => {
        if (!cancelled && d && typeof d === 'object') setUser(d)
      })
      .catch(() => {
        if (!cancelled) setUser(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [loggedIn])

  return { user: loggedIn ? user : null, loading: loggedIn && loading }
}
