import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import styles from './MapView.module.css'

function MapView({
  center = [-15.7942, -48.0192], // Brasília default
  zoom = 5,
  markers = [],
  onMapReady = null,
  onMarkerClick = null,
  showControls = true,
  height = '500px'
}) {
  const mapContainer = useRef(null)
  const map = useRef(null)
  const markersRef = useRef({})

  // Initialize map
  useEffect(() => {
    if (map.current) return

    map.current = L.map(mapContainer.current).setView(center, zoom)

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
      minZoom: 2,
    }).addTo(map.current)

    // Custom marker icon fix for webpack
    delete L.Icon.Default.prototype._getIconUrl
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    })

    if (onMapReady) {
      onMapReady(map.current)
    }

    return () => {
      // Cleanup on unmount
      if (map.current) {
        map.current.remove()
        map.current = null
      }
    }
  }, [])

  // Update markers
  useEffect(() => {
    if (!map.current) return

    // Clear old markers
    Object.values(markersRef.current).forEach(marker => {
      map.current.removeLayer(marker)
    })
    markersRef.current = {}

    // Add new markers
    markers.forEach((markerData) => {
      const { id, lat, lng, title, description, color = 'blue', type = 'default' } = markerData

      // Create custom icon based on type
      const iconColor = getIconColor(type, color)
      const customIcon = L.divIcon({
        className: `${styles.markerIcon} ${styles[`marker${iconColor}`]}`,
        html: `<div class="${styles.markerContent}">📍</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32],
      })

      const marker = L.marker([lat, lng], { icon: customIcon }).addTo(map.current)

      // Add popup
      if (title || description) {
        const popupContent = `
          <div class="${styles.popupContent}">
            ${title ? `<h4 class="${styles.popupTitle}">${title}</h4>` : ''}
            ${description ? `<p class="${styles.popupDescription}">${description}</p>` : ''}
            ${markerData.info ? `<div class="${styles.popupInfo}">${markerData.info}</div>` : ''}
          </div>
        `
        marker.bindPopup(popupContent)
      }

      // Add click handler
      marker.on('click', () => {
        if (onMarkerClick) {
          onMarkerClick(markerData)
        }
      })

      markersRef.current[id] = marker
    })

    // Auto-fit bounds if multiple markers
    if (markers.length > 1) {
      const group = new L.FeatureGroup(Object.values(markersRef.current))
      map.current.fitBounds(group.getBounds(), { padding: [50, 50] })
    }
  }, [markers, onMarkerClick])

  // Update center
  useEffect(() => {
    if (map.current && center) {
      map.current.setView(center, zoom)
    }
  }, [center, zoom])

  const getIconColor = (type, color) => {
    const typeMap = {
      'origem': 'Green',
      'destino': 'Red',
      'parada': 'Blue',
      'contrato': 'Purple',
      'default': 'Blue',
    }
    return typeMap[type] || typeMap.default
  }

  return (
    <div className={styles.mapContainer} style={{ height }}>
      <div className={styles.mapWrapper} ref={mapContainer} />
      {markers.length === 0 && (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>🗺️</div>
          <p>Nenhum marcador para exibir</p>
        </div>
      )}
    </div>
  )
}

export default MapView
