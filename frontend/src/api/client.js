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
  // Em produção a requisição tem de ir à API (Heroku), não ao site estático (Netlify, GitHub Pages, etc.)
  const baseEnv = (import.meta.env.VITE_API_URL || '').toString().trim()
  if (path.startsWith('/api') && !import.meta.env.DEV) {
    if (!baseEnv) {
      throw new Error(
        'Falta VITE_API_URL: no build (GitHub Actions, Netlify, etc.) defina a URL da API no Heroku (ex.: https://nomedapp.herokuapp.com, sem / no fim) e volte a publicar o site.',
      )
    }
    try {
      const u = new URL(baseEnv)
      const host = u.hostname
      if (
        (host.endsWith('netlify.app') || host === 'github.io' || host.endsWith('.github.io')) &&
        !host.includes('herokuapp.com')
      ) {
        throw new Error(
          'VITE_API_URL não pode ser o endereço do site estático. Use a URL do backend no Heroku, ex.: https://nomedapp.herokuapp.com (Heroku → Open app / Settings).',
        )
      }
    } catch (e) {
      if (e instanceof TypeError) {
        throw new Error('VITE_API_URL inválida. Use um endereço completo, ex.: https://minha-api.herokuapp.com')
      }
      throw e
    }
  }

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

  if (res.ok && typeof data === 'string' && /^\s*</.test(data)) {
    throw new Error(
      'A API devolveu HTML em vez de JSON. Confira o VITE_API_URL (URL do Heroku) no processo de build e faça um novo deploy do front.',
    )
  }

  if (!res.ok) {
    const detail =
      data && typeof data === 'object' && 'detail' in data
        ? formatDetail(data.detail)
        : res.statusText
    if (res.status === 404 && path.startsWith('/api')) {
      throw new Error(
        detail && detail !== 'Not Found'
          ? String(detail)
          : 'API não encontrada (404). Confira o VITE_API_URL (URL do Heroku no build) e se a API no Heroku está no ar.',
      )
    }
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
