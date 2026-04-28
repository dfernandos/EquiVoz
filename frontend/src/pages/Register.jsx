import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, setToken } from '../api/client'

const STORAGE_KEY = 'equivoz_conta_criada'

export default function Register() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api('/api/auth/register', {
        method: 'POST',
        json: { name, email, password },
      })
      const loginData = await api('/api/auth/login', {
        method: 'POST',
        json: { email, password },
      })
      if (data && data.mensagem) {
        try {
          sessionStorage.setItem(STORAGE_KEY, String(data.mensagem))
        } catch {
          /* ignore */
        }
      }
      setToken(loginData.access_token)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível cadastrar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page narrow">
      <h1 id="page-title">Criar conta</h1>
      <p className="muted">Nome ou apelido, e-mail e senha (mínimo 6 caracteres).</p>
      <p className="muted small">Depois de cadastrar, a sua sessão fica ativa; verá a confirmação na página inicial.</p>

      <form className="form" onSubmit={handleSubmit} aria-labelledby="page-title">
        {error ? (
          <div className="banner error" role="alert" aria-live="assertive">
            {error}
          </div>
        ) : null}

        <label htmlFor="name">Nome ou apelido</label>
        <input
          id="name"
          name="name"
          type="text"
          autoComplete="name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <label htmlFor="email">E-mail</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label htmlFor="password">Senha</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="new-password"
          required
          minLength={6}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="btn primary" type="submit" disabled={loading} aria-busy={loading}>
          {loading ? 'A criar…' : 'Criar conta e entrar'}
        </button>
      </form>

      <p className="muted small">
        Já tem conta? <Link to="/login">Entrar</Link>
      </p>
    </div>
  )
}
