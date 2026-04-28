import { useMemo } from 'react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { useColorMode } from '../context/ColorModeContext'

const PALETTE_PADRAO = [
  '#1e3d34',
  '#2d6a4f',
  '#40916c',
  '#52b788',
  '#74c69d',
  '#95d5b2',
  '#c9a227',
  '#e9c46a',
]

/** Tons com contrastes de matiz e luminância mais distintos (azul, laranja, violeta, âmbar…). */
const PALETTE_DALTONISMO = [
  '#1d4ed8',
  '#ea580c',
  '#7c3aed',
  '#ca8a04',
  '#be185d',
  '#0d9488',
  '#4f46e5',
  '#b45309',
]

function mesCurto(ym) {
  if (!ym || typeof ym !== 'string') return ym
  const [y, m] = ym.split('-')
  const n = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
  const i = parseInt(m, 10) - 1
  if (i < 0 || i > 11) return ym
  return `${n[i]}/${(y || '').slice(-2)}`
}

/**
 * @param {{ data: {
 *   total: number
 *   com_localizacao_mapa: number
 *   minhas: number
 *   por_tipo: { id: string, label: string, count: number }[]
 *   por_mes: { mes: string, registros: number }[]
 *   top_empresas: { empresa: string, total: number, minhas: number }[]
 * } | null, showPersonalKpi?: boolean } } props
 */
export default function DashboardPanel({ data, showPersonalKpi = true }) {
  const { isDaltonismo } = useColorMode()

  const { palette, areaFill, areaStroke, pieComMapa, pieSemMapa, gradId, uiBorder } = useMemo(() => {
    const cvd = isDaltonismo
    return {
      palette: cvd ? PALETTE_DALTONISMO : PALETTE_PADRAO,
      areaFill: cvd ? '#1d4ed8' : '#2d6a4f',
      areaStroke: cvd ? '#0c4a6e' : '#1e3d34',
      pieComMapa: cvd ? '#1d4ed8' : '#2d6a4f',
      pieSemMapa: cvd ? '#94a3b8' : '#b8b3ab',
      gradId: cvd ? 'evAreaGradCvd' : 'evAreaGradDef',
      uiBorder: cvd ? '#94a3b8' : '#c4bfb6',
    }
  }, [isDaltonismo])

  if (!data) return null

  const mapaOutros = Math.max(0, data.total - data.com_localizacao_mapa)
  const mapaPizza = [
    { name: 'Com local no mapa', value: data.com_localizacao_mapa, key: 'mapa' },
    { name: 'Só registro (sem pin)', value: mapaOutros, key: 'sem' },
  ]

  const barrasTipo = (data.por_tipo || []).map((t) => ({
    nome: t.label.length > 22 ? `${t.label.slice(0, 20)}…` : t.label,
    nomeFull: t.label,
    ocorrencias: t.count,
  }))

  const areaMes = (data.por_mes || []).map((r) => ({
    label: mesCurto(r.mes),
    registros: r.registros,
  }))

  return (
    <div className="dashboard-panel">
      <div className="dashboard-kpi-grid" role="group" aria-label="Resumo em números">
        <div className="dashboard-kpi">
          <span className="dashboard-kpi-label">Total no sistema</span>
          <strong className="dashboard-kpi-value">{data.total}</strong>
          <span className="dashboard-kpi-hint">denúncias</span>
        </div>
        {showPersonalKpi ? (
          <div className="dashboard-kpi">
            <span className="dashboard-kpi-label">Suas</span>
            <strong className="dashboard-kpi-value">{data.minhas}</strong>
            <span className="dashboard-kpi-hint">que você registrou</span>
          </div>
        ) : null}
        <div className="dashboard-kpi">
          <span className="dashboard-kpi-label">No mapa</span>
          <strong className="dashboard-kpi-value">{data.com_localizacao_mapa}</strong>
          <span className="dashboard-kpi-hint">com latitude e longitude</span>
        </div>
        <div className="dashboard-kpi dashboard-kpi--accent">
          <span className="dashboard-kpi-label">Cobertura do mapa</span>
          <strong className="dashboard-kpi-value">
            {data.total > 0
              ? `${Math.round((100 * data.com_localizacao_mapa) / data.total)}%`
              : '—'}
          </strong>
          <span className="dashboard-kpi-hint">dos relatos com pin</span>
        </div>
      </div>

      <div className="dashboard-charts-grid">
        <div className="dashboard-chart-card">
          <h3 className="dashboard-chart-title">
            Denúncias por mês (data da ocorrência ou de registro, se não houver ocorrência)
          </h3>
          {areaMes.length === 0 ? (
            <p className="dashboard-chart-empty muted">Ainda sem série temporal.</p>
          ) : (
            <div className="dashboard-chart-plot" role="img" aria-label="Gráfico de denúncias por mês">
              <ResponsiveContainer width="100%" height="100%" minHeight={240}>
                <AreaChart data={areaMes} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={areaFill} stopOpacity={0.35} />
                      <stop offset="100%" stopColor={areaFill} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ddd8" />
                  <XAxis dataKey="label" tick={{ fontSize: 12 }} tickLine={false} />
                  <YAxis allowDecimals={false} width={36} tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ borderRadius: 8, border: `1px solid ${uiBorder}` }}
                    formatter={(v) => [v, 'registros']}
                  />
                  <Area
                    type="monotone"
                    dataKey="registros"
                    stroke={areaStroke}
                    strokeWidth={2}
                    fill={`url(#${gradId})`}
                    name="Registros"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="dashboard-chart-card">
          <h3 className="dashboard-chart-title">Tipos de violação</h3>
          {barrasTipo.length === 0 ? (
            <p className="dashboard-chart-empty muted">Ainda sem dados por tipo.</p>
          ) : (
            <div className="dashboard-chart-plot" role="img" aria-label="Gráfico de barras por tipo de violação">
              <ResponsiveContainer width="100%" height="100%" minHeight={260}>
                <BarChart
                  data={barrasTipo}
                  margin={{ top: 8, right: 8, left: 0, bottom: 64 }}
                >
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ddd8" />
                  <XAxis
                    dataKey="nome"
                    tick={{ fontSize: 10 }}
                    interval={0}
                    angle={-35}
                    textAnchor="end"
                    height={70}
                  />
                  <YAxis allowDecimals={false} width={32} tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ borderRadius: 8, border: `1px solid ${uiBorder}` }}
                    formatter={(v) => [v, 'Ocorrências']}
                    labelFormatter={(_, p) => p[0]?.payload?.nomeFull ?? ''}
                  />
                  <Bar dataKey="ocorrencias" name="Ocorrências" radius={[4, 4, 0, 0]}>
                    {barrasTipo.map((_, i) => (
                      <Cell key={i} fill={palette[i % palette.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="dashboard-chart-card dashboard-chart-card--pie">
          <h3 className="dashboard-chart-title">Mapa: com pin vs. só registro</h3>
          {data.total === 0 ? (
            <p className="dashboard-chart-empty muted">Nenhum dado ainda.</p>
          ) : (
            <div
              className="dashboard-chart-plot dashboard-chart-plot--pie"
              role="img"
              aria-label="Proporção com e sem coordenadas"
            >
              <ResponsiveContainer width="100%" height="100%" minHeight={280}>
                <PieChart margin={{ top: 16, right: 16, bottom: 8, left: 16 }}>
                  <Pie
                    data={mapaPizza}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="48%"
                    innerRadius="42%"
                    outerRadius="70%"
                    paddingAngle={2}
                  >
                    {mapaPizza.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? pieComMapa : pieSemMapa} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ borderRadius: 8, border: `1px solid ${uiBorder}` }}
                    formatter={(value, name) => {
                      const n = Number(value)
                      const t = data.total
                      const pct = t > 0 ? ` (${((n / t) * 100).toFixed(0)}% do total)` : ''
                      return [
                        `${n} ocorrência${n === 1 ? '' : 's'}${pct}`,
                        name,
                      ]
                    }}
                  />
                  <Legend
                    layout="vertical"
                    verticalAlign="bottom"
                    align="center"
                    wrapperStyle={{ paddingTop: 12, fontSize: 13 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
