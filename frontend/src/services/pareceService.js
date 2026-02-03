import api from './api'

/**
 * Parecer Service - API calls for legal opinions/parecer
 */

/**
 * Buscar parecer de um contrato
 * GET /parecer/:id
 * @param {string} parecerId - ID do parecer
 * @returns {Promise} Dados completos do parecer
 */
export const fetchParecer = async (parecerId) => {
  try {
    const response = await api.get(`/parecer/${parecerId}`)
    return response.data
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error('Parecer não encontrado')
    }
    throw new Error(error.message || 'Erro ao buscar parecer')
  }
}

/**
 * Buscar parecer por contrato ID
 * GET /parecer?contrato_id=:id
 * @param {string} contratoId - ID do contrato
 * @returns {Promise} Parecer do contrato
 */
export const fetchParecerByContrato = async (contratoId) => {
  try {
    const response = await api.get('/parecer', {
      params: { contrato_id: contratoId },
    })
    return response.data.data[0] // Assuming returns array
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar parecer do contrato')
  }
}

/**
 * Listar todos os pareceres com filtros
 * GET /parecer
 * @param {Object} params - Query parameters
 *   - page: number
 *   - limit: number
 *   - verdict: string ('aprovado' | 'com_ressalvas' | 'reprovado')
 *   - status: string ('concluído' | 'processando' | 'erro')
 *   - search: string (buscar por contrato ID ou nome)
 * @returns {Promise} Lista de pareceres
 */
export const fetchPareceres = async (params = {}) => {
  try {
    const defaultParams = {
      page: 1,
      limit: 10,
      ...params,
    }
    const response = await api.get('/parecer', { params: defaultParams })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar pareceres')
  }
}

/**
 * Gerar parecer para um contrato
 * POST /parecer
 * @param {string} contratoId - ID do contrato
 * @param {Object} options - Opções de geração
 *   - force_regenerate: boolean
 *   - include_geo: boolean
 *   - include_bureau: boolean
 * @returns {Promise} Parecer gerado
 */
export const generateParecer = async (contratoId, options = {}) => {
  try {
    const response = await api.post('/parecer', {
      contrato_id: contratoId,
      ...options,
    })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao gerar parecer')
  }
}

/**
 * Atualizar parecer
 * PUT /parecer/:id
 * @param {string} parecerId - ID do parecer
 * @param {Object} updates - Dados a atualizar
 * @returns {Promise} Parecer atualizado
 */
export const updateParecer = async (parecerId, updates) => {
  try {
    const response = await api.put(`/parecer/${parecerId}`, updates)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao atualizar parecer')
  }
}

/**
 * Deletar parecer
 * DELETE /parecer/:id
 * @param {string} parecerId - ID do parecer
 * @returns {Promise} Confirmação de deleção
 */
export const deleteParecer = async (parecerId) => {
  try {
    const response = await api.delete(`/parecer/${parecerId}`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao deletar parecer')
  }
}

/**
 * Download parecer em PDF
 * GET /parecer/:id/download
 * @param {string} parecerId - ID do parecer
 * @param {string} filename - Nome do arquivo (default: parecer.pdf)
 */
export const downloadParecer = async (parecerId, filename = 'parecer.pdf') => {
  try {
    const response = await api.get(`/parecer/${parecerId}/download`, {
      responseType: 'blob',
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.parentElement.removeChild(link)
    window.URL.revokeObjectURL(url)

    return true
  } catch (error) {
    throw new Error(error.message || 'Erro ao baixar parecer')
  }
}

/**
 * Buscar achados/findings de um parecer
 * GET /parecer/:id/findings
 * @param {string} parecerId - ID do parecer
 * @returns {Promise} Lista de achados
 */
export const fetchFindings = async (parecerId) => {
  try {
    const response = await api.get(`/parecer/${parecerId}/findings`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar achados')
  }
}

/**
 * Buscar timeline de processamento
 * GET /parecer/:id/timeline
 * @param {string} parecerId - ID do parecer
 * @returns {Promise} Timeline de etapas
 */
export const fetchTimeline = async (parecerId) => {
  try {
    const response = await api.get(`/parecer/${parecerId}/timeline`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar timeline')
  }
}

/**
 * Buscar estatísticas de pareceres
 * GET /parecer/stats
 * @returns {Promise} Estatísticas
 */
export const fetchParecerStats = async () => {
  try {
    const response = await api.get('/parecer/stats')
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar estatísticas')
  }
}
