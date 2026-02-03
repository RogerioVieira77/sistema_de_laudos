import { useState, useCallback, useEffect } from 'react'

export function useMap(initialCenter = [-15.7942, -48.0192], initialZoom = 5) {
  const [center, setCenter] = useState(initialCenter)
  const [zoom, setZoom] = useState(initialZoom)
  const [markers, setMarkers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedMarker, setSelectedMarker] = useState(null)

  // Fetch locations from API
  const fetchLocations = useCallback(async (filters = {}) => {
    setLoading(true)
    setError(null)

    try {
      // Aqui integramos com a API de geolocalização quando disponível
      // Por enquanto, retornamos dados de exemplo
      const mockData = [
        {
          id: '1',
          lat: -15.7942,
          lng: -48.0192,
          title: 'Brasília - DF',
          description: 'Capital Federal',
          type: 'origem',
          info: '1.234 contratos',
        },
        {
          id: '2',
          lat: -23.5505,
          lng: -46.6333,
          title: 'São Paulo - SP',
          description: 'Maior metrópole',
          type: 'destino',
          info: '5.678 contratos',
        },
        {
          id: '3',
          lat: -30.0346,
          lng: -51.2177,
          title: 'Porto Alegre - RS',
          description: 'Capital do RS',
          type: 'parada',
          info: '890 contratos',
        },
      ]

      setMarkers(mockData)
    } catch (err) {
      setError(err.message || 'Erro ao buscar localizações')
      setMarkers([])
    } finally {
      setLoading(false)
    }
  }, [])

  // Add marker
  const addMarker = useCallback((markerData) => {
    setMarkers((prevMarkers) => [
      ...prevMarkers,
      {
        id: Date.now().toString(),
        type: 'default',
        ...markerData,
      },
    ])
  }, [])

  // Remove marker
  const removeMarker = useCallback((id) => {
    setMarkers((prevMarkers) => prevMarkers.filter((m) => m.id !== id))
  }, [])

  // Update marker
  const updateMarker = useCallback((id, updates) => {
    setMarkers((prevMarkers) =>
      prevMarkers.map((m) => (m.id === id ? { ...m, ...updates } : m))
    )
  }, [])

  // Clear all markers
  const clearMarkers = useCallback(() => {
    setMarkers([])
  }, [])

  // Set center
  const setMapCenter = useCallback((newCenter, newZoom = null) => {
    setCenter(newCenter)
    if (newZoom !== null) {
      setZoom(newZoom)
    }
  }, [])

  // Zoom in
  const zoomIn = useCallback(() => {
    setZoom((prevZoom) => Math.min(prevZoom + 1, 19))
  }, [])

  // Zoom out
  const zoomOut = useCallback(() => {
    setZoom((prevZoom) => Math.max(prevZoom - 1, 2))
  }, [])

  // Fit bounds to all markers
  const fitBounds = useCallback(() => {
    if (markers.length === 0) return

    if (markers.length === 1) {
      setMapCenter([markers[0].lat, markers[0].lng], 10)
      return
    }

    // Calculate bounds
    const lats = markers.map((m) => m.lat)
    const lngs = markers.map((m) => m.lng)
    const minLat = Math.min(...lats)
    const maxLat = Math.max(...lats)
    const minLng = Math.min(...lngs)
    const maxLng = Math.max(...lngs)

    // Center of bounds
    const centerLat = (minLat + maxLat) / 2
    const centerLng = (minLng + maxLng) / 2

    // Calculate appropriate zoom level
    const latDiff = maxLat - minLat
    const lngDiff = maxLng - minLng
    const maxDiff = Math.max(latDiff, lngDiff)

    let zoomLevel = 10
    if (maxDiff > 10) zoomLevel = 5
    else if (maxDiff > 5) zoomLevel = 6
    else if (maxDiff > 2) zoomLevel = 8
    else if (maxDiff > 1) zoomLevel = 9

    setMapCenter([centerLat, centerLng], zoomLevel)
  }, [markers, setMapCenter])

  // Calculate distance between two points (Haversine formula)
  const calculateDistance = useCallback((lat1, lng1, lat2, lng2) => {
    const R = 6371 // Earth radius in km
    const dLat = ((lat2 - lat1) * Math.PI) / 180
    const dLng = ((lng2 - lng1) * Math.PI) / 180
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }, [])

  // Get distance between two markers
  const getMarkerDistance = useCallback(
    (id1, id2) => {
      const marker1 = markers.find((m) => m.id === id1)
      const marker2 = markers.find((m) => m.id === id2)

      if (!marker1 || !marker2) return null

      return calculateDistance(marker1.lat, marker1.lng, marker2.lat, marker2.lng)
    },
    [markers, calculateDistance]
  )

  // Handle marker click
  const handleMarkerClick = useCallback((markerData) => {
    setSelectedMarker(markerData)
  }, [])

  // Auto-fetch on mount
  useEffect(() => {
    fetchLocations()
  }, [])

  return {
    // State
    center,
    zoom,
    markers,
    loading,
    error,
    selectedMarker,

    // Methods
    fetchLocations,
    addMarker,
    removeMarker,
    updateMarker,
    clearMarkers,
    setMapCenter,
    zoomIn,
    zoomOut,
    fitBounds,
    calculateDistance,
    getMarkerDistance,
    handleMarkerClick,
  }
}
