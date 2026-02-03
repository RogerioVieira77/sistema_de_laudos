import api from './api'

/**
 * Contract Service - API calls for contracts
 */

/**
 * Upload de arquivo contrato com progresso
 * POST /contratos/upload
 * @param {File} file - Arquivo PDF a ser enviado
 * @param {Function} onProgress - Callback para atualizar progresso
 * @returns {Promise} Resposta com ID do contrato
 */
export const uploadContract = async (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post('/contratos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(percentCompleted)
        }
      },
    })

    return response.data
  } catch (error) {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail)
    } else if (error.response?.status === 413) {
      throw new Error('Arquivo muito grande. Limite máximo: 10MB')
    } else if (error.response?.status === 415) {
      throw new Error('Tipo de arquivo não suportado. Use PDF.')
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Tempo limite de upload excedido')
    } else if (!error.response) {
      throw new Error('Erro de conexão com servidor')
    } else {
      throw new Error(error.message || 'Erro ao enviar arquivo')
    }
  }
}

/**
 * Buscar lista de contratos com filtros, busca, ordenação e paginação
 * GET /contratos
 * @param {Object} params - Query parameters
 *   - page: number (default: 1)
 *   - limit: number (default: 10)
 *   - sort_by: string (default: 'created_at')
 *   - sort_order: 'asc' | 'desc' (default: 'desc')
 *   - status: string (comma-separated list)
 *   - search: string (filename or ID)
 * @returns {Promise} Lista de contratos com paginação
 */
export const fetchContratos = async (params = {}) => {
  try {
    const defaultParams = {
      page: 1,
      limit: 10,
      sort_by: 'created_at',
      sort_order: 'desc',
      ...params,
    }

    const response = await api.get('/contratos', { params: defaultParams })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar contratos')
  }
}

/**
 * Buscar contrato específico com resultado
 * GET /contratos/:id
 * @param {string} contratoId - ID do contrato
 * @returns {Promise} Dados do contrato com análise e parecer
 */
export const fetchContratoById = async (contratoId) => {
  try {
    const response = await api.get(`/contratos/${contratoId}`)
    return response.data
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error('Contrato não encontrado')
    }
    throw new Error(error.message || 'Erro ao buscar contrato')
  }
}

/**
 * Deletar contrato
 * DELETE /contratos/:id
 * @param {string} contratoId - ID do contrato
 * @returns {Promise} Confirmação de deleção
 */
export const deleteContrato = async (contratoId) => {
  try {
    const response = await api.delete(`/contratos/${contratoId}`)
    return response.data
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error('Contrato não encontrado')
    }
    throw new Error(error.message || 'Erro ao deletar contrato')
  }
}

/**
 * Buscar parecer de um contrato
 * GET /contratos/:id/parecer
 * @param {string} contratoId - ID do contrato
 * @returns {Promise} Parecer jurídico completo
 */
export const fetchParecerByContrato = async (contratoId) => {
  try {
    const response = await api.get(`/contratos/${contratoId}/parecer`)
    return response.data
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error('Parecer não encontrado')
    }
    throw new Error(error.message || 'Erro ao buscar parecer')
  }
}

/**
 * Buscar geolocalização de um contrato
 * GET /contratos/:id/geolocalizacao
 * @param {string} contratoId - ID do contrato
 * @returns {Promise} Dados de geolocalização
 */
export const fetchGeoByContrato = async (contratoId) => {
  try {
    const response = await api.get(`/contratos/${contratoId}/geolocalizacao`)
    return response.data
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error('Geolocalização não encontrada')
    }
    throw new Error(error.message || 'Erro ao buscar geolocalização')
  }
}

/**
 * Download parecer em PDF
 * GET /contratos/:id/parecer/download
 * @param {string} contratoId - ID do contrato
 * @param {string} filename - Nome do arquivo a salvar (opcional)
 */
export const downloadParecer = async (contratoId, filename = 'parecer.pdf') => {
  try {
    const response = await api.get(`/contratos/${contratoId}/parecer/download`, {
      responseType: 'blob',
    })

    // Create blob link to download
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
 * Exportar contrato com resultado
 * GET /contratos/:id/export
 * @param {string} contratoId - ID do contrato
 * @param {string} format - 'json' | 'csv' | 'xlsx' (default: 'json')
 */
export const exportContrato = async (contratoId, format = 'json') => {
  try {
    const response = await api.get(`/contratos/${contratoId}/export`, {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    })

    if (format !== 'json') {
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      const extension = format === 'csv' ? 'csv' : 'xlsx'
      link.setAttribute('download', `contrato-${contratoId}.${extension}`)
      document.body.appendChild(link)
      link.click()
      link.parentElement.removeChild(link)
      window.URL.revokeObjectURL(url)
    }

    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao exportar contrato')
  }
}

/**
 * Buscar estatísticas
 * GET /contratos/stats
 * @returns {Promise} Estatísticas dos contratos
 */
export const fetchStats = async () => {
  try {
    const response = await api.get('/contratos/stats')
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar estatísticas')
  }
}
