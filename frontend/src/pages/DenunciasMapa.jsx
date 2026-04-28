import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import DenunciasMap from '../components/DenunciasMap'

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
  } catch {
    return '—'
  }
}

function useDebounced(value, delay) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return debounced
}

function buildQuery(filtroEmpresa, filtroTipo, dataInicio, dataFim) {
  const p = new URLSearchParams()
  if (filtroEmpresa.trim()) p.set('empresa', filtroEmpresa.trim())
  if (filtroTipo) p.set('violation_type', filtroTipo)
  if (dataInicio) p.set('data_inicio', dataInicio)
  if (dataFim) p.set('data_fim', dataFim)
  const s = p.toString()
  return s ? `?${s}` : ''
}

export default function DenunciasMapa() {
  const [searchParams] = useSearchParams()
  const [rows, setRows] = useState([])
  const [tipos, setTipos] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [empresaInput, setEmpresaInput] = useState(
    () => (searchParams.get('empresa') || '').trim(),
  )
  const [tipo, setTipo] = useState('')
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim] = useState('')
  const [meId, setMeId] = useState(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const u = await api('/api/auth/me')
        if (!cancelled && u && typeof u.id === 'number') setMeId(u.id)
      } catch {
        if (!cancelled) setMeId(null)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    const fromUrl = (searchParams.get('empresa') || '').trim()
    if (fromUrl) setEmpresaInput(fromUrl)
  }, [searchParams])

  const debouncedEmpresa = useDebounced(empresaInput, 400)
  const queryString = useMemo(
    () => buildQuery(debouncedEmpresa, tipo, dataInicio, dataFim),
    [debouncedEmpresa, tipo, dataInicio, dataFim],
  )

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setError('')
      setLoading(true)
      try {
        const [tipoList, list] = await Promise.all([
          api('/api/denuncias/tipos-violacao'),
          api(`/api/denuncias${queryString}`),
        ])
        if (cancelled) return
        if (Array.isArray(tipoList)) setTipos(tipoList)
        setRows(Array.isArray(list) ? list : [])
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : 'Não foi possível carregar as denúncias e filtros.',
          )
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [queryString])

  const labelById = useMemo(() => {
    const m = new Map()
    for (const t of tipos) m.set(t.id, t.label)
    return m
  }, [tipos])

  const mapMarkers = useMemo(() => {
    const out = []
    for (const d of rows) {
      const lat = d.latitude
      const lng = d.longitude
      if (lat == null || lng == null) continue
      if (Number.isNaN(Number(lat)) || Number.isNaN(Number(lng))) continue
      out.push({
        id: d.id,
        position: [Number(lat), Number(lng)],
        title: d.title,
        label: labelById.get(d.violation_type) ?? d.violation_type,
        empresa: d.empresa?.trim() || null,
        description: d.description,
      })
    }
    return out
  }, [rows, labelById])

  const comCoordenadas = mapMarkers.length
  const semCoordenadas = rows.length - comCoordenadas

  function limparFiltros() {
    setEmpresaInput('')
    setTipo('')
    setDataInicio('')
    setDataFim('')
  }

  const apagarDenuncia = useCallback(
    async (id) => {
      if (
        !window.confirm(
          'Excluir esta denúncia permanentemente? Não será possível desfazer depois de confirmar.',
        )
      ) {
        return
      }
      try {
        await api(`/api/denuncias/${id}`, { method: 'DELETE' })
        setRows((prev) => prev.filter((r) => r.id !== id))
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Falha ao excluir.')
      }
    },
    [],
  )

  return (
    <div className="page page--mapa">
      <h1 id="page-title">Denúncias</h1>
      <p className="muted">
        Filtre por trecho (empresa, título ou local), tipo e intervalo de datas. A data considera
        a ocorrência informada ou, se não houver, a data de registro.
      </p>

      <div className="denuncias-filtros" role="search" aria-label="Filtros de denúncias">
        <div className="denuncias-filtros-row">
          <div className="denuncias-filtros-field">
            <label htmlFor="filtro-empresa">Empresa / título / local</label>
            <input
              id="filtro-empresa"
              type="search"
              value={empresaInput}
              onChange={(e) => setEmpresaInput(e.target.value)}
              placeholder="Ex.: Habbibs"
              autoComplete="off"
            />
          </div>
          <div className="denuncias-filtros-field">
            <label htmlFor="filtro-tipo">Tipo de denúncia</label>
            <select
              id="filtro-tipo"
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
            >
              <option value="">Todos</option>
              {tipos.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="denuncias-filtros-row">
          <div className="denuncias-filtros-field">
            <label htmlFor="filtro-inicio">Data inicial</label>
            <input
              id="filtro-inicio"
              type="date"
              value={dataInicio}
              onChange={(e) => setDataInicio(e.target.value)}
            />
          </div>
          <div className="denuncias-filtros-field">
            <label htmlFor="filtro-fim">Data final</label>
            <input
              id="filtro-fim"
              type="date"
              value={dataFim}
              onChange={(e) => setDataFim(e.target.value)}
            />
          </div>
          <div className="denuncias-filtros-actions">
            <button type="button" className="btn secondary" onClick={limparFiltros}>
              Limpar filtros
            </button>
          </div>
        </div>
      </div>

      {error ? (
        <div className="banner error" role="alert" aria-live="assertive">
          {error}
        </div>
      ) : null}

      {loading ? (
        <p className="muted" role="status" aria-live="polite">
          Carregando…
        </p>
      ) : null}

      {!loading && !error ? (
        <p className="denuncias-map-meta muted small">
          {rows.length} {rows.length === 1 ? 'registro' : 'registros'}
          {semCoordenadas > 0
            ? ` · ${comCoordenadas} no mapa, ${semCoordenadas} sem coordenadas`
            : comCoordenadas > 0
              ? ' · todos com localização no mapa'
              : ' · nenhum com localização no mapa'}
        </p>
      ) : null}

      <section className="denuncias-map-block" aria-labelledby="titulo-mapa">
        <h2 className="denuncias-section-title" id="titulo-mapa">
          Mapa
        </h2>
        {loading ? null : <DenunciasMap markers={mapMarkers} />}
      </section>

      <section className="denuncias-lista-block" aria-labelledby="titulo-lista">
        <h2 className="denuncias-section-title" id="titulo-lista">
          Lista
        </h2>
        {loading || error ? null : rows.length === 0 ? (
          <p className="muted">
            Nenhuma denúncia com estes filtros. <Link to="/denuncia">Registrar ocorrência</Link>
          </p>
        ) : (
          <ul className="denuncias-lista">
            {rows.map((d) => (
              <li key={d.id} className="denuncias-item">
                <div className="denuncias-item-head">
                  <span className="denuncias-item-title">{d.title}</span>
                  <span className="denuncias-item-badge">
                    {labelById.get(d.violation_type) ?? d.violation_type}
                  </span>
                </div>
                {d.empresa ? <p className="denuncias-item-empresa">{d.empresa}</p> : null}
                <p className="denuncias-item-desc">{d.description}</p>
                <dl className="denuncias-item-meta">
                  <div>
                    <dt>Registrado em</dt>
                    <dd>{formatDate(d.created_at)}</dd>
                  </div>
                  {d.occurred_at ? (
                    <div>
                      <dt>Ocorrência</dt>
                      <dd>{formatDate(d.occurred_at)}</dd>
                    </div>
                  ) : null}
                  <div>
                    <dt>Local</dt>
                    <dd>{d.location_text?.trim() || '—'}</dd>
                  </div>
                  <div>
                    <dt>Mapa</dt>
                    <dd>
                      {d.latitude != null && d.longitude != null
                        ? `${d.latitude}, ${d.longitude}`
                        : '—'}
                    </dd>
                  </div>
                </dl>
                {meId != null && d.user_id === meId ? (
                  <div className="denuncias-item-actions">
                    <Link
                      className="btn secondary small"
                      to={`/denuncia/${d.id}/edit`}
                      aria-label={`Editar denúncia: ${d.title}`}
                    >
                      Editar
                    </Link>
                    <button
                      type="button"
                      className="btn danger small"
                      onClick={() => apagarDenuncia(d.id)}
                      aria-label={`Excluir denúncia: ${d.title}`}
                    >
                      Excluir
                    </button>
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>

      <p className="muted small" style={{ marginTop: '1.5rem' }}>
        <Link to="/denuncia">Nova denúncia</Link> · <Link to="/">Início</Link>
      </p>
    </div>
  )
}
