import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import DashboardPanel from '../components/DashboardPanel'
import { useAuth } from '../hooks/useAuth'

export default function Home() {
  const loggedIn = useAuth()
  const [dashboard, setDashboard] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setError('')
      setLoading(true)
      try {
        const d = await api('/api/denuncias/estatisticas/dashboard')
        if (!cancelled) setDashboard(d && typeof d === 'object' ? d : null)
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Não foi possível carregar o painel.')
          setDashboard(null)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [loggedIn])

  const topEmpresas = Array.isArray(dashboard?.top_empresas) ? dashboard.top_empresas : []
  const minhas = dashboard?.minhas ?? 0

  return (
    <div className="page page--dashboard page--home-dashboard">
      <header className="home-dashboard-header">
        <h1 id="page-title">EquiVoz</h1>
        <p className="lead home-dashboard-lead">
          Registro de ocorrências relacionadas à discriminação e violações de direitos, com foco em
          minorias sociais. Abaixo, estatísticas públicas agregadas (totais, tendências e
          estabelecimentos com mais relatos) — em tempo real, sem precisar de conta.
        </p>
        <div className="actions home-dashboard-cta">
          {loggedIn ? (
            <>
              <Link className="btn primary" to="/denuncia">
                Nova denúncia
              </Link>
              <Link className="btn secondary" to="/denuncias">
                Mapa e lista
              </Link>
            </>
          ) : (
            <>
              <Link className="btn primary" to="/login">
                Entrar
              </Link>
              <Link className="btn secondary" to="/cadastro">
                Criar conta
              </Link>
            </>
          )}
        </div>
      </header>

      {error ? (
        <div className="banner error" role="alert" aria-live="assertive">
          {error}
        </div>
      ) : null}

      {loading ? <p className="muted">Carregando o painel…</p> : null}

      {!loading && !error && dashboard ? (
        <>
          {loggedIn && minhas > 0 ? (
            <p className="dashboard-inline-summary muted">
              Sua contagem: <strong>{minhas}</strong>{' '}
              {minhas === 1 ? 'denúncia registrada' : 'denúncias registradas'} por você.
            </p>
          ) : null}
          <DashboardPanel data={dashboard} showPersonalKpi={loggedIn} />
        </>
      ) : null}

      {!loading && !error && dashboard && (
        <section
          className="dashboard-section dashboard-section--table"
          aria-label="Tabela de estabelecimentos com mais registro de denúncias"
        >
          <h2 className="dashboard-section-title">Onde mais há denúncias (empresa ou título)</h2>
          <p className="muted small dashboard-hint">
            Cada linha agrega ocorrências pelo <strong>nome de empresa</strong> ou pelo{' '}
            <strong>título</strong> quando a empresa veio só no título.
            {loggedIn ? (
              <>
                {' '}
                A coluna “Suas” indica as suas ocorrências naquele grupo. Para o nome de
                estabelecimento, use o campo no cadastro.
              </>
            ) : null}
          </p>
          {topEmpresas.length === 0 ? (
            <p className="muted">
              Ainda não há denúncias.{' '}
              {loggedIn ? (
                <Link to="/denuncia">Registre uma ocorrência</Link>
              ) : (
                <>
                  <Link to="/login">Entre</Link> ou <Link to="/cadastro">crie uma conta</Link> para
                  registrar.
                </>
              )}
            </p>
          ) : (
            <div className="table-wrap">
              <table className="dashboard-table">
                <caption className="visually-hidden">Ranking de estabelecimentos</caption>
                <thead>
                  <tr>
                    <th scope="col">#</th>
                    <th scope="col">Estabelecimento</th>
                    <th scope="col">Total</th>
                    {loggedIn ? <th scope="col">Suas</th> : null}
                    <th scope="col">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {topEmpresas.map((row, i) => (
                    <tr key={`${row.empresa}-${i}`}>
                      <td>{i + 1}</td>
                      <td>
                        <strong>{row.empresa}</strong>
                        {loggedIn && row.minhas > 0 ? (
                          <span className="dashboard-you-badge" title="Você tem denúncia neste grupo">
                            você
                          </span>
                        ) : null}
                      </td>
                      <td>{row.total}</td>
                      {loggedIn ? <td>{row.minhas}</td> : null}
                      <td>
                        {loggedIn ? (
                          <Link
                            to={`/denuncias?empresa=${encodeURIComponent(row.empresa)}`}
                            className="dashboard-link"
                          >
                            Ver no mapa
                          </Link>
                        ) : (
                          <Link to="/login" className="dashboard-link">
                            Entre para ver no mapa
                          </Link>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

    </div>
  )
}
