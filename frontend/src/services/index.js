/**
 * Services Index - Unified export of all API services
 * Makes imports cleaner and more maintainable
 */

// API configuration
export { default as api, setTokens, clearTokens, getUser, getAccessToken, isAuthenticated } from './api'

// Contract Service
export {
  uploadContract,
  fetchContratos,
  fetchContratoById,
  deleteContrato,
  fetchParecerByContrato,
  fetchGeoByContrato,
  downloadParecer,
  exportContrato,
  fetchStats,
} from './contractService'

// Parecer Service
export {
  fetchParecer,
  fetchParecerByContrato as fetchParecerFromService,
  fetchPareceres,
  generateParecer,
  updateParecer,
  deleteParecer,
  downloadParecer as downloadParecerService,
  fetchFindings,
  fetchTimeline,
  fetchParecerStats,
} from './pareceService'

// Geo Service
export {
  fetchLocations,
  reverseGeocode,
  geocodeAddress,
  calculateDistance,
  searchLocations,
  createLocation,
  updateLocation,
  deleteLocation,
} from './geoService'

// Bureau Service
export {
  fetchBureau,
  fetchBureaus,
  fetchScore,
  fetchHistory,
  fetchRestrictions,
  fetchAggregated,
  analyzeScores,
  fetchTrends,
  exportBureau,
} from './bureauService'
