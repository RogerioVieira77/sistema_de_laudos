import { useEffect, useRef } from 'react'
import L from 'leaflet'
import styles from './MapMarker.module.css'

/**
 * MapMarker Component
 * Renderiza um marcador individual no mapa
 * Este é um componente auxiliar para ser usado dentro de MapView
 */
function MapMarker({
  map,
  id,
  lat,
  lng,
  title,
  description,
  type = 'default',
  color = 'blue',
  icon = '📍',
  draggable = false,
  onDrag = null,
  onClick = null,
  onRemove = null,
}) {
  const markerRef = useRef(null)

  useEffect(() => {
    if (!map || !map.current) return

    // Get icon color
    const iconColor = getIconColor(type, color)

    // Create custom icon
    const customIcon = L.divIcon({
      className: `${styles.markerIcon} ${styles[`marker${iconColor}`]}`,
      html: `<div class="${styles.markerContent}">${icon}</div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -32],
    })

    // Create marker
    const marker = L.marker([lat, lng], {
      icon: customIcon,
      draggable: draggable,
    }).addTo(map.current)

    // Add popup
    if (title || description) {
      const popupContent = `
        <div class="${styles.popupContent}">
          ${title ? `<h4 class="${styles.popupTitle}">${title}</h4>` : ''}
          ${description ? `<p class="${styles.popupDescription}">${description}</p>` : ''}
        </div>
      `
      marker.bindPopup(popupContent)
    }

    // Event handlers
    if (onClick) {
      marker.on('click', () => {
        onClick({ id, lat, lng, title, description })
      })
    }

    if (draggable && onDrag) {
      marker.on('dragend', (event) => {
        const newLat = event.target.getLatLng().lat
        const newLng = event.target.getLatLng().lng
        onDrag({ id, lat: newLat, lng: newLng })
      })
    }

    markerRef.current = marker

    return () => {
      if (markerRef.current) {
        map.current.removeLayer(markerRef.current)
      }
    }
  }, [map, lat, lng, title, description, type, color, icon, draggable, onClick, onDrag])

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

  const getLatLng = () => {
    if (markerRef.current) {
      return markerRef.current.getLatLng()
    }
    return { lat, lng }
  }

  const setPosition = (newLat, newLng) => {
    if (markerRef.current) {
      markerRef.current.setLatLng([newLat, newLng])
    }
  }

  const openPopup = () => {
    if (markerRef.current) {
      markerRef.current.openPopup()
    }
  }

  const closePopup = () => {
    if (markerRef.current) {
      markerRef.current.closePopup()
    }
  }

  const remove = () => {
    if (markerRef.current && map.current) {
      map.current.removeLayer(markerRef.current)
      if (onRemove) {
        onRemove(id)
      }
    }
  }

  // Public methods
  useEffect(() => {
    if (markerRef.current) {
      markerRef.current.getLatLng = getLatLng
      markerRef.current.setPosition = setPosition
      markerRef.current.openPopup = openPopup
      markerRef.current.closePopup = closePopup
      markerRef.current.remove = remove
    }
  }, [])

  return null // Este componente apenas renderiza no mapa via Leaflet
}

export default MapMarker
