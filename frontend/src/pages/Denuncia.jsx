import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'

function isoToDatetimeLocalValue(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

export default function Denuncia() {
  const { id: routeId } = useParams()
  const navigate = useNavigate()
  const isEdit = routeId != null && routeId !== ''
  const denunciaId = isEdit ? routeId : null

  const [tipos, setTipos] = useState([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [violationType, setViolationType] = useState('')
  const [occurredAt, setOccurredAt] = useState('')
  const [empresa, setEmpresa] = useState('')
  const [locationText, setLocationText] = useState('')
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [message, setMessage] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingTipos, setLoadingTipos] = useState(true)
  const [loadingRecord, setLoadingRecord] = useState(isEdit)
  const [loadError, setLoadError] = useState('')
  const [deleting, setDeleting] = useState(false)
  const [geocoding, setGeocoding] = useState(false)
  const [geocodeHint, setGeocodeHint] = useState('')

  useEffect(() => {
    if (message) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [message])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const data = await api('/api/denuncias/tipos-violacao')
        if (!cancelled && Array.isArray(data)) {
          setTipos(data)
          if (data.length && !violationType && !isEdit) setViolationType(data[0].id)
        }
      } catch {
        if (!cancelled) setError('Não foi possível carregar os tipos de ocorrência.')
      } finally {
        if (!cancelled) setLoadingTipos(false)
      }
    })()
    return () => {
      cancelled = true
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- predefinir 1.º tipo só em novo registro
  }, [isEdit])

  useEffect(() => {
    if (!isEdit || !denunciaId) {
      setLoadingRecord(false)
      return
    }
    let cancelled = false
    ;(async () => {
      setLoadError('')
      setLoadingRecord(true)
      try {
        const d = await api(`/api/denuncias/${denunciaId}`)
        if (cancelled) return
        setTitle(d.title || '')
        setDescription(d.description || '')
        setViolationType(d.violation_type || '')
        setEmpresa(d.empresa || '')
        setLocationText(d.location_text || '')
        setLatitude(d.latitude != null ? String(d.latitude) : '')
        setLongitude(d.longitude != null ? String(d.longitude) : '')
        setOccurredAt(isoToDatetimeLocalValue(d.occurred_at))
        setGeocodeHint('')
      } catch (e) {
        if (!cancelled) {
          setLoadError(
            e instanceof Error
              ? e.message
              : 'Não foi possível carregar a denúncia. Verifique se é o registro que você criou.',
          )
        }
      } finally {
        if (!cancelled) setLoadingRecord(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [isEdit, denunciaId])

  async function buscarCoordenadasPeloEndereco() {
    const q = locationText.trim()
    setError('')
    setGeocodeHint('')
    if (q.length < 3) {
      setError('Escreva o endereço (mínimo 3 caracteres) antes de buscar no mapa.')
      return
    }
    setGeocoding(true)
    try {
      const params = new URLSearchParams({ q })
      const res = await api(`/api/geocoding/search?${params.toString()}`)
      if (res && res.encontrado && typeof res.latitude === 'number' && typeof res.longitude === 'number') {
        setLatitude(String(res.latitude))
        setLongitude(String(res.longitude))
        setGeocodeHint(
          res.endereco_exibido
            ? `Local encontrado: ${res.endereco_exibido.slice(0, 180)}${res.endereco_exibido.length > 180 ? '…' : ''}`
            : 'Coordenadas preenchidas. Confira no mapa ao enviar a denúncia.',
        )
      } else if (res && res.encontrado === false) {
        setError(res.mensagem || 'Não encontramos coordenadas para este endereço.')
      } else {
        setError('Resposta inesperada do serviço de endereços.')
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Falha ao buscar o endereço.')
    } finally {
      setGeocoding(false)
    }
  }

  function buildPayload() {
    return {
      title: title.trim(),
      description: description.trim(),
      violation_type: violationType,
      empresa: empresa.trim() || null,
      occurred_at: occurredAt ? new Date(occurredAt).toISOString() : null,
      location_text: locationText.trim() || null,
      latitude: latitude === '' ? null : Number(latitude),
      longitude: longitude === '' ? null : Number(longitude),
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setMessage(null)
    setLoading(true)

    const payload = buildPayload()

    if (
      payload.latitude != null &&
      (Number.isNaN(payload.latitude) || payload.longitude == null || Number.isNaN(payload.longitude))
    ) {
      setError('Se informar latitude, informe também longitude com valores numéricos válidos.')
      setLoading(false)
      return
    }
    if (
      payload.longitude != null &&
      (Number.isNaN(payload.longitude) || payload.latitude == null || Number.isNaN(payload.latitude))
    ) {
      setError('Se informar longitude, informe também latitude com valores numéricos válidos.')
      setLoading(false)
      return
    }

    try {
      if (isEdit && denunciaId) {
        await api(`/api/denuncias/${denunciaId}`, { method: 'PUT', json: payload })
        setMessage('Denúncia atualizada com sucesso.')
      } else {
        await api('/api/denuncias', { method: 'POST', json: payload })
        setMessage('Denúncia registrada com sucesso.')
        setTitle('')
        setDescription('')
        setEmpresa('')
        setOccurredAt('')
        setLocationText('')
        setLatitude('')
        setLongitude('')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao enviar')
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete() {
    if (!isEdit || !denunciaId) return
    if (
      !window.confirm(
        'Excluir esta denúncia permanentemente? Não será possível desfazer depois de confirmar.',
      )
    ) {
      return
    }
    setDeleting(true)
    setError('')
    try {
      await api(`/api/denuncias/${denunciaId}`, { method: 'DELETE' })
      navigate('/denuncias', { replace: true })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Falha ao excluir.')
    } finally {
      setDeleting(false)
    }
  }

  const formDisabled = loadingTipos || (isEdit && (loadingRecord || loadError))

  return (
    <div className="page">
      <h1 id="page-title">{isEdit ? 'Editar ocorrência' : 'Registrar ocorrência'}</h1>
      {isEdit ? (
        <p className="muted">
          Altere os campos e salve, ou exclua o registro. Só quem criou a denúncia pode editá-la ou
          excluí-la.
        </p>
      ) : (
        <p className="muted">
          Descreva o que ocorreu. Data, hora e local são opcionais. Se preencher o endereço, pode
          carregar em <strong>Usar endereço no mapa</strong> para sugerir latitude e longitude
          (OpenStreetMap), sem as escrever à mão. Evidências em arquivo ficam para uma próxima etapa.
        </p>
      )}

      {isEdit && loadingRecord ? (
        <p className="muted" role="status" aria-live="polite">
          Carregando denúncia…
        </p>
      ) : null}
      {loadError ? (
        <div className="banner error" role="alert" aria-live="assertive">
          {loadError} <Link to="/denuncias">Voltar à lista</Link>
        </div>
      ) : null}

      {loadingTipos ? (
        <p className="muted" role="status" aria-live="polite">
          Carregando…
        </p>
      ) : null}
      {loadError ? null : (
        <form className="form" onSubmit={handleSubmit} aria-labelledby="page-title">
        {message ? (
          <div className="banner success" role="status" aria-live="polite">
            {message}{' '}
            {isEdit ? <Link to="/denuncias">Ver na lista</Link> : <Link to="/">Voltar ao início</Link>}
          </div>
        ) : null}
        {error ? (
          <div className="banner error" role="alert" aria-live="assertive">
            {error}
          </div>
        ) : null}

        <label htmlFor="title">Título resumido</label>
        <input
          id="title"
          name="title"
          type="text"
          required
          minLength={3}
          maxLength={500}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={formDisabled}
        />

        <label htmlFor="empresa">Empresa ou estabelecimento (opcional)</label>
        <input
          id="empresa"
          name="empresa"
          type="text"
          maxLength={255}
          value={empresa}
          onChange={(e) => setEmpresa(e.target.value)}
          disabled={formDisabled}
          placeholder="Ex.: nome do comércio, hospital, escola"
        />

        <label htmlFor="violation_type">Tipo de violação</label>
        <select
          id="violation_type"
          name="violation_type"
          required
          value={violationType}
          onChange={(e) => setViolationType(e.target.value)}
          disabled={formDisabled}
        >
          {tipos.map((t) => (
            <option key={t.id} value={t.id}>
              {t.label}
            </option>
          ))}
        </select>

        <label htmlFor="description">Descrição</label>
        <textarea
          id="description"
          name="description"
          rows={6}
          required
          minLength={10}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={formDisabled}
          placeholder="Relate o contexto com o máximo de detalhes que se sentir confortável em compartilhar."
        />

        <label htmlFor="occurred_at">Data e hora aproximadas (opcional)</label>
        <input
          id="occurred_at"
          name="occurred_at"
          type="datetime-local"
          value={occurredAt}
          onChange={(e) => setOccurredAt(e.target.value)}
          disabled={formDisabled}
        />

        <label htmlFor="location_text">Local / endereço descritivo (opcional)</label>
        <input
          id="location_text"
          name="location_text"
          type="text"
          maxLength={500}
          value={locationText}
          onChange={(e) => {
            setLocationText(e.target.value)
            setGeocodeHint('')
          }}
          disabled={formDisabled}
        />
        <div className="geocode-row">
          <button
            type="button"
            className="btn secondary"
            onClick={buscarCoordenadasPeloEndereco}
            disabled={geocoding || formDisabled}
            aria-describedby="geocode-hint"
            aria-busy={geocoding}
          >
            {geocoding ? 'Buscando endereço…' : 'Usar endereço no mapa'}
          </button>
          <span className="geocode-hint muted small" id="geocode-hint">
            Sugere o pin a partir do texto (Brasil, via OpenStreetMap).
          </span>
        </div>
        {geocodeHint ? (
          <div className="banner success geocode-hint-box" role="status" aria-live="polite">
            {geocodeHint}
          </div>
        ) : null}

        <fieldset className="coords" disabled={formDisabled}>
          <legend>Coordenadas (opcional)</legend>
          <p className="coords-help muted small">
            Pode preencher manualmente ou deixar o botão acima completar a partir do endereço.
          </p>
          <div className="row">
            <div>
              <label htmlFor="latitude">Latitude</label>
              <input
                id="latitude"
                name="latitude"
                type="text"
                inputMode="decimal"
                value={latitude}
                onChange={(e) => {
                  setLatitude(e.target.value)
                  setGeocodeHint('')
                }}
                placeholder="-23.55"
              />
            </div>
            <div>
              <label htmlFor="longitude">Longitude</label>
              <input
                id="longitude"
                name="longitude"
                type="text"
                inputMode="decimal"
                value={longitude}
                onChange={(e) => {
                  setLongitude(e.target.value)
                  setGeocodeHint('')
                }}
                placeholder="-46.63"
              />
            </div>
          </div>
        </fieldset>

        <div className="denuncia-form-footer">
          {isEdit && denunciaId ? (
            <button
              type="button"
              className="btn danger"
              onClick={handleDelete}
              disabled={deleting || loading || formDisabled}
              aria-busy={deleting}
            >
              {deleting ? 'Excluindo…' : 'Excluir denúncia'}
            </button>
          ) : null}
          <button
            className="btn primary"
            type="submit"
            disabled={loading || formDisabled}
            aria-busy={loading}
          >
            {loading
              ? isEdit
                ? 'Salvando…'
                : 'Enviando…'
              : isEdit
                ? 'Salvar'
                : 'Registrar denúncia'}
          </button>
        </div>
      </form>
      )}
    </div>
  )
}
