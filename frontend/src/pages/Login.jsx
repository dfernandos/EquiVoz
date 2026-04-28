import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, setToken } from '../api/client'

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [reenviarEmail, setReenviarEmail] = useState('')
  const [reenviarStatus, setReenviarStatus] = useState('')
  const [reenviarLoad, setReenviarLoad] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api('/api/auth/login', {
        method: 'POST',
        json: { email, password },
      })
      setToken(data.access_token)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha no login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page narrow">
      <h1 id="page-title">Entrar</h1>
      <p className="muted">Use seu e-mail e senha para acessar o sistema.</p>

      <form className="form" onSubmit={handleSubmit} aria-labelledby="page-title">
        {error ? (
          <div className="banner error" role="alert" aria-live="assertive">
            {error}
          </div>
        ) : null}

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
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button className="btn primary" type="submit" disabled={loading} aria-busy={loading}>
          {loading ? 'Entrando…' : 'Entrar'}
        </button>
      </form>

      <div className="form secondary-block">
        <p className="muted small" id="reenviar-label">
          Ainda sem confirmação de e-mail? Reenviamos o link.
        </p>
        <div className="row-inline">
          <input
            type="email"
            name="reenviar"
            autoComplete="email"
            placeholder="O seu e-mail de cadastro"
            value={reenviarEmail}
            onChange={(e) => setReenviarEmail(e.target.value)}
            aria-labelledby="reenviar-label"
          />
          <button
            className="btn secondary"
            type="button"
            disabled={reenviarLoad || !reenviarEmail.trim()}
            onClick={async () => {
              setReenviarStatus('')
              setReenviarLoad(true)
              try {
                const d = await api('/api/auth/reenviar-verificacao', {
                  method: 'POST',
                  json: { email: reenviarEmail.trim() },
                })
                if (d && d.detail) setReenviarStatus(String(d.detail))
              } catch (e) {
                setReenviarStatus(e instanceof Error ? e.message : 'Falha')
              } finally {
                setReenviarLoad(false)
              }
            }}
          >
            {reenviarLoad ? 'A enviar…' : 'Reenviar'}
          </button>
        </div>
        {reenviarStatus ? <p className="muted small">{reenviarStatus}</p> : null}
      </div>

      <p className="muted small">
        Não tem conta? <Link to="/cadastro">Cadastre-se</Link>
      </p>
    </div>
  )
}
