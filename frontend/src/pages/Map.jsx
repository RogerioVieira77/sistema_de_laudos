import { useState } from 'react'
import MainLayout from '../components/layouts/MainLayout'
import MapView from '../components/map/MapView'
import MapControls from '../components/map/MapControls'
import { useMap } from '../hooks/useMap'
import styles from './Map.module.css'

function Map() {
  const {
    center,
    zoom,
    markers,
    loading,
    error,
    selectedMarker,
    fetchLocations,
    addMarker,
    removeMarker,
    setMapCenter,
    zoomIn,
    zoomOut,
    fitBounds,
    getMarkerDistance,
    handleMarkerClick,
  } = useMap()

  const [mapRef, setMapRef] = useState(null)
  const [expandedInfo, setExpandedInfo] = useState(true)

  const handleMapReady = (map) => {
    setMapRef(map)
  }

  const handleAddMarker = () => {
    // Exemplo: adicionar novo marcador no centro do mapa
    addMarker({
      lat: center[0],
      lng: center[1],
      title: 'Novo Marcador',
      description: 'Clique para editar',
      type: 'default',
    })
  }

  const handleFitBounds = () => {
    fitBounds()
  }

  const handleRemoveMarker = (id) => {
    removeMarker(id)
    setExpandedInfo(false)
  }

  return (
    <MainLayout activeItem="mapa">
      <div className={styles.page}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.titleSection}>
            <h1 className={styles.title}>🗺️ Mapa de Contratos</h1>
            <p className={styles.subtitle}>
              Visualize a distribuição geográfica de seus contratos
            </p>
          </div>
          <div className={styles.stats}>
            <div className={styles.statCard}>
              <span className={styles.statLabel}>Total de Locais</span>
              <span className={styles.statValue}>{markers.length}</span>
            </div>
            <div className={styles.statCard}>
              <span className={styles.statLabel}>Zoom Atual</span>
              <span className={styles.statValue}>{zoom}</span>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className={styles.errorMessage}>
            <span>❌ {error}</span>
          </div>
        )}

        {/* Main Content */}
        <div className={styles.container}>
          {/* Map Section */}
          <main className={styles.mapSection}>
            <MapView
              center={center}
              zoom={zoom}
              markers={markers}
              onMapReady={handleMapReady}
              onMarkerClick={handleMarkerClick}
              height="600px"
            />
            <MapControls
              map={{ current: mapRef }}
              centerCoords={center}
              onCenterMap={handleFitBounds}
            />
          </main>

          {/* Info Sidebar */}
          {expandedInfo && (
            <aside className={styles.infoSidebar}>
              <div className={styles.infoHeader}>
                <h3>ℹ️ Informações</h3>
                <button
                  className={styles.closeBtn}
                  onClick={() => setExpandedInfo(false)}
                >
                  ✕
                </button>
              </div>

              {selectedMarker ? (
                <div className={styles.markerInfo}>
                  <div className={styles.markerTitle}>{selectedMarker.title}</div>
                  <div className={styles.markerDescription}>
                    {selectedMarker.description}
                  </div>

                  {selectedMarker.info && (
                    <div className={styles.markerStats}>
                      <div className={styles.statItem}>
                        <span className={styles.statLabel}>Informação</span>
                        <span className={styles.statText}>
                          {selectedMarker.info}
                        </span>
                      </div>
                    </div>
                  )}

                  <div className={styles.coordinates}>
                    <div className={styles.coordItem}>
                      <span>Latitude:</span>
                      <span className={styles.coordValue}>
                        {selectedMarker.lat.toFixed(6)}
                      </span>
                    </div>
                    <div className={styles.coordItem}>
                      <span>Longitude:</span>
                      <span className={styles.coordValue}>
                        {selectedMarker.lng.toFixed(6)}
                      </span>
                    </div>
                  </div>

                  {/* Distance to other markers */}
                  {markers.filter((m) => m.id !== selectedMarker.id).length > 0 && (
                    <div className={styles.distances}>
                      <h4>Distâncias</h4>
                      {markers
                        .filter((m) => m.id !== selectedMarker.id)
                        .map((marker) => {
                          const distance = getMarkerDistance(
                            selectedMarker.id,
                            marker.id
                          )
                          return (
                            <div key={marker.id} className={styles.distanceItem}>
                              <span>{marker.title}</span>
                              <span className={styles.distanceValue}>
                                {distance ? `${distance.toFixed(2)} km` : 'N/A'}
                              </span>
                            </div>
                          )
                        })}
                    </div>
                  )}

                  <div className={styles.actions}>
                    <button
                      className={styles.actionBtn}
                      onClick={() => handleRemoveMarker(selectedMarker.id)}
                    >
                      🗑️ Remover
                    </button>
                  </div>
                </div>
              ) : (
                <div className={styles.noSelection}>
                  <div className={styles.noSelectionIcon}>👆</div>
                  <p>Clique em um marcador para ver detalhes</p>
                </div>
              )}

              {/* Markers List */}
              <div className={styles.markersList}>
                <h4 className={styles.listTitle}>Marcadores ({markers.length})</h4>
                <div className={styles.listContent}>
                  {markers.map((marker) => (
                    <div
                      key={marker.id}
                      className={`${styles.listItem} ${
                        selectedMarker?.id === marker.id ? styles.active : ''
                      }`}
                      onClick={() => handleMarkerClick(marker)}
                    >
                      <span className={styles.markerType}>{marker.type}</span>
                      <span className={styles.markerName}>{marker.title}</span>
                    </div>
                  ))}
                </div>
              </div>
            </aside>
          )}
        </div>

        {/* Bottom Actions */}
        <div className={styles.actions}>
          <button className={styles.actionBtn} onClick={handleFitBounds}>
            📍 Ajustar Visualização
          </button>
          <button className={styles.actionBtn} onClick={handleAddMarker}>
            ➕ Adicionar Marcador
          </button>
        </div>
      </div>
    </MainLayout>
  )
}

export default Map
