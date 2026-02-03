import api from './api'

/**
 * Geolocation Service - API calls for geolocation data
 */

/**
 * Buscar localizações de um contrato
 * GET /geolocalizacao/:contrato_id
 * @param {string} contratoId - ID do contrato
 * @returns {Promise} Lista de localizações
 */
export const fetchLocations = async (contratoId) => {
  try {
    const response = await api.get(`/geolocalizacao/${contratoId}`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar localizações')
  }
}

/**
 * Buscar endereço por coordenadas (reverse geocoding)
 * GET /geolocalizacao/reverse
 * @param {number} latitude - Latitude
 * @param {number} longitude - Longitude
 * @returns {Promise} Dados de endereço
 */
export const reverseGeocode = async (latitude, longitude) => {
  try {
    const response = await api.get('/geolocalizacao/reverse', {
      params: { latitude, longitude },
    })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao fazer reverse geocoding')
  }
}

/**
 * Geocodificar endereço (coordinates a partir de endereço)
 * GET /geolocalizacao/geocode
 * @param {string} address - Endereço completo
 * @returns {Promise} Dados de coordenadas
 */
export const geocodeAddress = async (address) => {
  try {
    const response = await api.get('/geolocalizacao/geocode', {
      params: { address },
    })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao geocodificar endereço')
  }
}

/**
 * Calcular distância entre dois pontos
 * POST /geolocalizacao/distance
 * @param {Object} from - Ponto de origem { latitude, longitude }
 * @param {Object} to - Ponto de destino { latitude, longitude }
 * @returns {Promise} Distância em km e metros
 */
export const calculateDistance = async (from, to) => {
  try {
    const response = await api.post('/geolocalizacao/distance', { from, to })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao calcular distância')
  }
}

/**
 * Buscar todas as localizações com filtros
 * GET /geolocalizacao
 * @param {Object} params - Query parameters
 *   - type: string ('origem' | 'destino' | 'parada')
 *   - latitude: number (para busca por proximidade)
 *   - longitude: number
 *   - radius: number (raio em km)
 * @returns {Promise} Lista de localizações
 */
export const searchLocations = async (params = {}) => {
  try {
    const response = await api.get('/geolocalizacao', { params })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar localizações')
  }
}

/**
 * Criar nova localização
 * POST /geolocalizacao
 * @param {Object} location - Dados da localização
 *   - address: string
 *   - latitude: number
 *   - longitude: number
 *   - type: string ('origem' | 'destino' | 'parada')
 *   - contrato_id: string (optional)
 * @returns {Promise} Localização criada
 */
export const createLocation = async (location) => {
  try {
    const response = await api.post('/geolocalizacao', location)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao criar localização')
  }
}

/**
 * Atualizar localização
 * PUT /geolocalizacao/:id
 * @param {string} id - ID da localização
 * @param {Object} updates - Dados a atualizar
 * @returns {Promise} Localização atualizada
 */
export const updateLocation = async (id, updates) => {
  try {
    const response = await api.put(`/geolocalizacao/${id}`, updates)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao atualizar localização')
  }
}

/**
 * Deletar localização
 * DELETE /geolocalizacao/:id
 * @param {string} id - ID da localização
 * @returns {Promise} Confirmação de deleção
 */
export const deleteLocation = async (id) => {
  try {
    const response = await api.delete(`/geolocalizacao/${id}`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao deletar localização')
  }
}
