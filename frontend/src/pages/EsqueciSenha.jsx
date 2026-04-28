import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

export default function EsqueciSenha() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [enviado, setEnviado] = useState(false)
  const [mensagem, setMensagem] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await api('/api/auth/esqueci-senha', {
        method: 'POST',
        json: { email: email.trim() },
      })
      if (data && data.detail) setMensagem(String(data.detail))
      setEnviado(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível enviar o pedido')
    } finally {
      setLoading(false)
    }
  }

  if (enviado) {
    return (
      <div className="page narrow">
        <h1 id="page-title">Verifique o e-mail</h1>
        <p className="banner success" role="status" aria-live="polite">
          {mensagem ||
            'Se existir uma conta com este e-mail, enviaremos as instruções para redefinir a senha.'}
        </p>
        <p className="muted small">Confira também a pasta de spam.</p>
        <p className="muted small">
          <Link to="/login">Voltar para entrar</Link>
        </p>
      </div>
    )
  }

  return (
    <div className="page narrow">
      <h1 id="page-title">Esqueci a senha</h1>
      <p className="muted">Informe o e-mail da sua conta. Se existir cadastro, enviaremos um link para criar uma nova senha.</p>

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

        <button className="btn primary" type="submit" disabled={loading} aria-busy={loading}>
          {loading ? 'Enviando…' : 'Enviar link'}
        </button>
      </form>

      <p className="muted small">
        <Link to="/login">Voltar para entrar</Link>
      </p>
    </div>
  )
}
