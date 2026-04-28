import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'

export default function VerifyEmail() {
  const [params] = useSearchParams()
  const token = (params.get('token') || '').trim()
  const [status, setStatus] = useState(() => (token ? 'pendente' : 'erro'))
  const [mensagem, setMensagem] = useState(() =>
    token ? '' : 'Link inválido: token em falta.',
  )

  useEffect(() => {
    if (!token) return
    let cancel = false
    ;(async () => {
      try {
        const data = await api(`/api/auth/verificar-email?token=${encodeURIComponent(token)}`)
        if (cancel) return
        if (data && typeof data === 'object' && 'detail' in data) {
          setMensagem(String(data.detail))
          setStatus('ok')
        } else {
          setStatus('ok')
          setMensagem('E-mail confirmado.')
        }
      } catch (e) {
        if (cancel) return
        setStatus('erro')
        setMensagem(e instanceof Error ? e.message : 'Não foi possível confirmar o e-mail.')
      }
    })()
    return () => {
      cancel = true
    }
  }, [token])

  return (
    <div className="page narrow">
      <h1 id="page-title">Confirmar e-mail</h1>
      {status === 'pendente' ? <p className="muted">A processar o link…</p> : null}
      {status === 'ok' ? (
        <p className="banner success" role="status">
          {mensagem}
        </p>
      ) : null}
      {status === 'erro' ? (
        <p className="banner error" role="alert">
          {mensagem}
        </p>
      ) : null}
      {status === 'ok' || status === 'erro' ? (
        <p>
          <Link to="/login" className="btn primary">
            Ir para entrar
          </Link>
        </p>
      ) : null}
    </div>
  )
}
