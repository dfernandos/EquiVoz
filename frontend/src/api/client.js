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
  // Em produção o pedido tem de ir ao Heroku, não ao próprio Netlify.
  const baseEnv = (import.meta.env.VITE_API_URL || '').toString().trim()
  if (path.startsWith('/api') && !import.meta.env.DEV) {
    if (!baseEnv) {
      throw new Error(
        'Configuração em falta: defina VITE_API_URL no Netlify com a URL da API no Heroku (…herokuapp.com, sem / no fim) e volte a fazer o deploy.',
      )
    }
    try {
      const u = new URL(baseEnv)
      if (u.hostname.endsWith('netlify.app') && !u.hostname.includes('herokuapp.com')) {
        throw new Error(
          'VITE_API_URL não pode ser o endereço do site (Netlify). Coloque a URL do backend no Heroku, por exemplo: https://o-nome-da-sua-app.herokuapp.com (vê no dashboard da Heroku → Open app / Settings → Domains).',
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
      'A API devolveu HTML em vez de JSON. No Netlify, defina VITE_API_URL com a URL do Heroku e faça um novo build.',
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
          : 'API não encontrada (404). Confirme VITE_API_URL no Netlify e se a API no Heroku está a correr.',
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
