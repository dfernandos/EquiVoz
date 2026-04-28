import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [registou, setRegistou] = useState(false)
  const [reenviarLoading, setReenviarLoading] = useState(false)
  const [reenviarMsg, setReenviarMsg] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api('/api/auth/register', {
        method: 'POST',
        json: { name, email, password },
      })
      if (data && data.mensagem) {
        setReenviarMsg(String(data.mensagem))
      }
      setRegistou(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível cadastrar')
    } finally {
      setLoading(false)
    }
  }

  async function reenviar() {
    if (!email.trim()) return
    setReenviarMsg('')
    setReenviarLoading(true)
    try {
      const data = await api('/api/auth/reenviar-verificacao', {
        method: 'POST',
        json: { email: email.trim() },
      })
      if (data && data.detail) setReenviarMsg(String(data.detail))
    } catch (e) {
      setReenviarMsg(e instanceof Error ? e.message : 'Falha ao reenviar')
    } finally {
      setReenviarLoading(false)
    }
  }

  if (registou) {
    return (
      <div className="page narrow">
        <h1 id="page-title">Conta criada</h1>
        <p className="banner success" role="status" aria-live="polite">
          {reenviarMsg || 'Verifique a sua caixa de entrada.'}
        </p>
        <p className="muted">
          Abra o <strong>link de confirmação</strong> no e-mail antes de <Link to="/login">entrar</Link>. Se não
          vir o e-mail, confira a pasta de spam.
        </p>
        <p>
          <button
            className="btn secondary"
            type="button"
            onClick={reenviar}
            disabled={reenviarLoading}
          >
            {reenviarLoading ? 'A enviar…' : 'Reenviar e-mail de confirmação'}
          </button>
        </p>
        <p className="muted small">
          <Link to="/">Voltar ao início</Link> · <Link to="/login">Página de entrar</Link>
        </p>
      </div>
    )
  }

  return (
    <div className="page narrow">
      <h1 id="page-title">Criar conta</h1>
      <p className="muted">Nome ou apelido, e-mail e senha (mínimo 6 caracteres).</p>
      <p className="muted small">
        Enviaremos um <strong>link de confirmação</strong> — só depois de confirmar poderá entrar.
      </p>

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
          {loading ? 'A criar…' : 'Criar conta e receber o link'}
        </button>
      </form>

      <p className="muted small">
        Já tem conta? <Link to="/login">Entrar</Link>
      </p>
    </div>
  )
}
