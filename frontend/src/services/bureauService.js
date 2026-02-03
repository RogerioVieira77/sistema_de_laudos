import api from './api'

/**
 * Bureau Service - API calls for bureau/credit data
 */

/**
 * Buscar dados de bureau para um contrato
 * GET /bureau/:contrato_id
 * @param {string} contratoId - ID do contrato
 * @returns {Promise} Dados de bureau
 */
export const fetchBureau = async (contratoId) => {
  try {
    const response = await api.get(`/bureau/${contratoId}`)
    return response.data
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error('Dados de bureau não encontrados')
    }
    throw new Error(error.message || 'Erro ao buscar dados de bureau')
  }
}

/**
 * Buscar todos os registros de bureau com filtros
 * GET /bureau
 * @param {Object} params - Query parameters
 *   - page: number
 *   - limit: number
 *   - contrato_id: string
 *   - score_min: number
 *   - score_max: number
 *   - status: string
 * @returns {Promise} Lista de registros
 */
export const fetchBureaus = async (params = {}) => {
  try {
    const defaultParams = {
      page: 1,
      limit: 10,
      ...params,
    }
    const response = await api.get('/bureau', { params: defaultParams })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar registros de bureau')
  }
}

/**
 * Buscar score de crédito específico
 * GET /bureau/:id/score
 * @param {string} bureauId - ID do registro de bureau
 * @returns {Promise} Dados de score
 */
export const fetchScore = async (bureauId) => {
  try {
    const response = await api.get(`/bureau/${bureauId}/score`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar score')
  }
}

/**
 * Buscar histórico de inquéritos
 * GET /bureau/:id/history
 * @param {string} bureauId - ID do registro de bureau
 * @returns {Promise} Histórico de inquéritos
 */
export const fetchHistory = async (bureauId) => {
  try {
    const response = await api.get(`/bureau/${bureauId}/history`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar histórico')
  }
}

/**
 * Buscar restrições/negativações
 * GET /bureau/:id/restrictions
 * @param {string} bureauId - ID do registro de bureau
 * @returns {Promise} Lista de restrições
 */
export const fetchRestrictions = async (bureauId) => {
  try {
    const response = await api.get(`/bureau/${bureauId}/restrictions`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar restrições')
  }
}

/**
 * Buscar dados agregados
 * GET /bureau/:id/aggregated
 * @param {string} bureauId - ID do registro de bureau
 * @returns {Promise} Dados agregados
 */
export const fetchAggregated = async (bureauId) => {
  try {
    const response = await api.get(`/bureau/${bureauId}/aggregated`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar dados agregados')
  }
}

/**
 * Análise comparativa de scores
 * POST /bureau/analysis
 * @param {Array} bureauIds - Lista de IDs para comparação
 * @returns {Promise} Análise comparativa
 */
export const analyzeScores = async (bureauIds) => {
  try {
    const response = await api.post('/bureau/analysis', { ids: bureauIds })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao analisar scores')
  }
}

/**
 * Buscar tendências de bureau
 * GET /bureau/trends
 * @param {Object} params - Query parameters
 *   - period: string ('7days' | '30days' | '90days' | '1year')
 * @returns {Promise} Tendências
 */
export const fetchTrends = async (params = {}) => {
  try {
    const response = await api.get('/bureau/trends', { params })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar tendências')
  }
}

/**
 * Exportar dados de bureau
 * GET /bureau/:id/export
 * @param {string} bureauId - ID do registro
 * @param {string} format - 'json' | 'csv' | 'pdf'
 */
export const exportBureau = async (bureauId, format = 'pdf') => {
  try {
    const response = await api.get(`/bureau/${bureauId}/export`, {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    })

    if (format !== 'json') {
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `bureau-${bureauId}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.parentElement.removeChild(link)
      window.URL.revokeObjectURL(url)
    }

    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao exportar dados')
  }
}
