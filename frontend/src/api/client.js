const API_BASE = import.meta.env.VITE_API_URL ?? ''

export const EQUIVOZ_AUTH_EVENT = 'equivoz-auth-changed'

export function getToken() {
  return localStorage.getItem('equivoz_token')
}

export function setToken(token) {
  if (token) localStorage.setItem('equivoz_token', token)
  else localStorage.removeItem('equivoz_token')
  window.dispatchEvent(new Event(EQUIVOZ_AUTH_EVENT))
}

/**
 * @param {string} path
 * @param {RequestInit & { json?: object }} options
 */
export async function api(path, options = {}) {
  const { json, ...fetchOpts } = options
  const headers = new Headers(fetchOpts.headers)

  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let body = fetchOpts.body
  if (json !== undefined) {
    headers.set('Content-Type', 'application/json')
    body = JSON.stringify(json)
  }

  const res = await fetch(`${API_BASE}${path}`, { ...fetchOpts, headers, body })

  const text = await res.text()
  let data = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  if (!res.ok) {
    const detail =
      data && typeof data === 'object' && 'detail' in data
        ? formatDetail(data.detail)
        : res.statusText
    throw new Error(detail || `Erro ${res.status}`)
  }

  return data
}

function formatDetail(detail) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((e) => (typeof e === 'object' && e.msg ? e.msg : String(e))).join('; ')
  }
  return JSON.stringify(detail)
}
