import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'

export default function RedefinirSenha() {
  const [searchParams] = useSearchParams()
  const fromQuery = (searchParams.get('token') || '').trim()
  const [token, setToken] = useState(fromQuery)
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [ok, setOk] = useState(false)
  const [detail, setDetail] = useState('')

  useEffect(() => {
    if (fromQuery) setToken(fromQuery)
  }, [fromQuery])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (password !== password2) {
      setError('As senhas não coincidem.')
      return
    }
    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres.')
      return
    }
    if (!token.trim()) {
      setError('Cole o link completo do e-mail ou o token do convite.')
      return
    }
    setLoading(true)
    try {
      const data = await api('/api/auth/redefinir-senha', {
        method: 'POST',
        json: { token: token.trim(), password },
      })
      if (data && data.detail) setDetail(String(data.detail))
      setOk(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível redefinir a senha')
    } finally {
      setLoading(false)
    }
  }

  if (ok) {
    return (
      <div className="page narrow">
        <h1 id="page-title">Senha alterada</h1>
        <p className="banner success" role="status" aria-live="polite">
          {detail || 'Senha redefinida com sucesso.'}
        </p>
        <p>
          <Link className="btn primary" to="/login">
            Entrar
          </Link>
        </p>
      </div>
    )
  }

  return (
    <div className="page narrow">
      <h1 id="page-title">Nova senha</h1>
      <p className="muted">Defina uma nova senha (mínimo 6 caracteres). O link enviado por e-mail expira após um tempo.</p>

      <form className="form" onSubmit={handleSubmit} aria-labelledby="page-title">
        {error ? (
          <div className="banner error" role="alert" aria-live="assertive">
            {error}
          </div>
        ) : null}

        {!fromQuery ? (
          <>
            <label htmlFor="token">Token</label>
            <input
              id="token"
              name="token"
              type="text"
              autoComplete="off"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Cole o token se abriu o link sem o parâmetro na barra de endereço"
            />
          </>
        ) : (
          <p className="muted small" role="status">
            Link do e-mail reconhecido. Defina a nova senha abaixo.
          </p>
        )}

        <label htmlFor="password">Nova senha</label>
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

        <label htmlFor="password2">Confirmar senha</label>
        <input
          id="password2"
          name="password2"
          type="password"
          autoComplete="new-password"
          required
          minLength={6}
          value={password2}
          onChange={(e) => setPassword2(e.target.value)}
        />

        <button className="btn primary" type="submit" disabled={loading} aria-busy={loading}>
          {loading ? 'Salvando…' : 'Redefinir senha'}
        </button>
      </form>

      <p className="muted small">
        <Link to="/login">Voltar para entrar</Link> · <Link to="/esqueci-senha">Pedir novo link</Link>
      </p>
    </div>
  )
}
