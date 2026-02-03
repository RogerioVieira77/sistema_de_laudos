import { useState } from 'react'
import { ZoomIn, ZoomOut, MapPin, Layers } from 'lucide-react'
import styles from './MapControls.module.css'

function MapControls({
  map,
  onZoomIn = null,
  onZoomOut = null,
  onCenterMap = null,
  centerCoords = null,
  onLayerToggle = null,
  layers = ['OpenStreetMap', 'Satellite'],
  currentLayer = 'OpenStreetMap',
}) {
  const [showLayersMenu, setShowLayersMenu] = useState(false)

  const handleZoomIn = () => {
    if (map && map.current) {
      map.current.zoomIn()
    }
    if (onZoomIn) onZoomIn()
  }

  const handleZoomOut = () => {
    if (map && map.current) {
      map.current.zoomOut()
    }
    if (onZoomOut) onZoomOut()
  }

  const handleCenter = () => {
    if (map && map.current && centerCoords) {
      map.current.setView(centerCoords, map.current.getZoom())
    }
    if (onCenterMap) onCenterMap()
  }

  const handleLayerChange = (layer) => {
    setShowLayersMenu(false)
    if (onLayerToggle) {
      onLayerToggle(layer)
    }
  }

  return (
    <div className={styles.controls}>
      {/* Zoom Controls */}
      <div className={styles.controlGroup}>
        <button
          className={styles.controlBtn}
          onClick={handleZoomIn}
          title="Aumentar zoom"
          aria-label="Aumentar zoom"
        >
          <ZoomIn size={20} />
        </button>
        <button
          className={styles.controlBtn}
          onClick={handleZoomOut}
          title="Diminuir zoom"
          aria-label="Diminuir zoom"
        >
          <ZoomOut size={20} />
        </button>
      </div>

      {/* Center Button */}
      {centerCoords && (
        <div className={styles.controlGroup}>
          <button
            className={styles.controlBtn}
            onClick={handleCenter}
            title="Centralizar mapa"
            aria-label="Centralizar mapa"
          >
            <MapPin size={20} />
          </button>
        </div>
      )}

      {/* Layer Toggle */}
      {layers && layers.length > 0 && (
        <div className={styles.controlGroup}>
          <button
            className={styles.controlBtn}
            onClick={() => setShowLayersMenu(!showLayersMenu)}
            title="Alternar camadas"
            aria-label="Alternar camadas"
          >
            <Layers size={20} />
          </button>

          {showLayersMenu && (
            <div className={styles.layersMenu}>
              {layers.map((layer) => (
                <button
                  key={layer}
                  className={`${styles.layerOption} ${
                    currentLayer === layer ? styles.active : ''
                  }`}
                  onClick={() => handleLayerChange(layer)}
                >
                  <span className={styles.layerName}>{layer}</span>
                  {currentLayer === layer && (
                    <span className={styles.checkmark}>✓</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Info Box */}
      <div className={styles.infoBox}>
        <div className={styles.infoLabel}>Coordenadas</div>
        <div className={styles.coordDisplay}>
          {centerCoords
            ? `${centerCoords[0].toFixed(4)}°, ${centerCoords[1].toFixed(4)}°`
            : 'Clique no mapa'}
        </div>
      </div>
    </div>
  )
}

export default MapControls
