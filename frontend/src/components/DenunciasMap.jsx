import { useEffect, useMemo } from 'react'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

import { useColorMode } from '../context/ColorModeContext'

function makePinIcon(fill, stroke) {
  return L.divIcon({
    className: 'denuncias-pin-outer',
    html: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="44" viewBox="0 0 24 36" aria-hidden="true">
  <path fill="${fill}" stroke="${stroke}" stroke-width="0.5" d="M12 0C6.4 0 2 4.1 2 9.1c0 5.3 4.2 10.2 7.2 15.1.4.6 1.1 1.1 1.8 1.1h.2c.7 0 1.3-.4 1.7-1 3.1-4.8 7.1-9.5 7.1-15.1C20 4.1 16.1 0 12 0z"/>
  <circle fill="#fff" cx="12" cy="9" r="3.2"/>
  </svg>`,
    iconSize: [32, 44],
    iconAnchor: [16, 44],
    popupAnchor: [0, -40],
  })
}

const BR_CENTER = [-14.23, -51.93]
const DEFAULT_Z = 4

/**
 * Ajusta o mapa às posições ou exibe o Brasil.
 * @param {{ id: string | number, position: [number, number] }[]} markers
 */
function MapBounds({ markers }) {
  const map = useMap()
  const key = markers.map((m) => `${m.id}:${m.position[0]}:${m.position[1]}`).join('|')

  useEffect(() => {
    const positions = markers.map((m) => m.position)
    if (positions.length === 0) {
      map.setView(BR_CENTER, DEFAULT_Z)
      return
    }
    if (positions.length === 1) {
      map.setView(positions[0], 12)
      return
    }
    const bounds = L.latLngBounds(positions)
    map.fitBounds(bounds, { padding: [40, 40] })
  }, [map, key])

  return null
}

/**
 * @param {{
 *   markers: {
 *     id: string | number
 *     position: [number, number]
 *     title: string
 *     label: string
 *     empresa: string | null
 *     description: string
 *   }[]
 * }} props
 */
export default function DenunciasMap({ markers }) {
  const { isDaltonismo } = useColorMode()
  const pinIcon = useMemo(
    () =>
      isDaltonismo
        ? makePinIcon('#1d4ed8', '#1e3a8a')
        : makePinIcon('#c42b1c', '#8b1a12'),
    [isDaltonismo],
  )

  return (
    <section
      className="leaflet-map-wrap"
      data-testid="denuncias-map"
      role="region"
      aria-label="Mapa interativo de ocorrências. Com o foco no mapa, use as setas do teclado para mover a vista e as teclas + e − para zoom."
    >
      <MapContainer
        center={BR_CENTER}
        zoom={DEFAULT_Z}
        scrollWheelZoom
        className="leaflet-map"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapBounds markers={markers} />
        {markers.map((m) => (
          <Marker key={m.id} position={m.position} icon={pinIcon}>
            <Popup
              className="denuncia-leaflet-popup"
              maxWidth={320}
              minWidth={220}
              autoPan
            >
              <div className="denuncia-popup-inner">
                <span className="map-popup-type">{m.label}</span>
                {m.empresa ? <div className="map-popup-empresa">{m.empresa}</div> : null}
                <div className="map-popup-title">{m.title}</div>
                {m.description ? (
                  <div className="map-popup-desc">{m.description}</div>
                ) : null}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </section>
  )
}
