import axios from 'axios'

// Usar a URL base do backend
const API_BASE_URL = '/api/v1'

// Track if we're already refreshing token to avoid multiple refresh requests
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  
  isRefreshing = false
  failedQueue = []
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutos para upload de arquivos grandes
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Request Interceptor - Injects access token into every request
 */
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

/**
 * Response Interceptor - Handles token refresh on 401 and global error handling
 */
api.interceptors.response.use(
  response => {
    return response
  },
  async error => {
    const originalRequest = error.config

    // Handle 401 - Unauthorized (token expired or invalid)
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch(err => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) {
          handleUnauthorized()
          return Promise.reject(error)
        }

        // Token refresh will be implemented with Keycloak
        // For now, just clear tokens and redirect to login
        handleUnauthorized()
        return Promise.reject(error)
      } catch (refreshError) {
        processQueue(refreshError, null)
        handleUnauthorized()
        return Promise.reject(refreshError)
      }
    }

    // Handle 403 - Forbidden
    if (error.response?.status === 403) {
      error.message = 'Você não tem permissão para acessar este recurso'
    }

    // Handle 404 - Not Found
    if (error.response?.status === 404) {
      error.message = 'Recurso não encontrado'
    }

    // Handle 500 - Server Error
    if (error.response?.status >= 500) {
      error.message = 'Erro no servidor. Tente novamente mais tarde.'
    }

    // Handle network errors
    if (!error.response && error.message !== 'canceled') {
      error.message = 'Erro de conexão com o servidor'
    }

    return Promise.reject(error)
  }
)

/**
 * Handle unauthorized - clear tokens and redirect to login
 */
function handleUnauthorized() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  
  // Dispatch custom event for components to listen
  window.dispatchEvent(new CustomEvent('unauthorized', { detail: { message: 'Sessão expirada' } }))
}

/**
 * Upload de arquivo contrato
 * @param {File} file - Arquivo PDF a ser enviado
 * @param {Function} onProgress - Callback para atualizar progresso (recebe { loaded, total })
 * @returns {Promise} Resposta do servidor
 */
export const uploadFile = async (file, onProgress) => {
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
    // Melhorar mensagem de erro
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
 * Buscar lista de contratos enviados
 * @param {number} page - Página (padrão: 1)
 * @param {number} limit - Itens por página (padrão: 10)
 * @param {string} sortBy - Campo para ordenação (padrão: 'created_at')
 * @param {string} sortOrder - 'asc' ou 'desc' (padrão: 'desc')
 * @param {Array} statuses - Array de status para filtrar (padrão: undefined)
 * @param {string} search - Buscar por filename ou ID (padrão: undefined)
 * @returns {Promise} Lista de contratos
 */
export const fetchContratos = async (
  page = 1,
  limit = 10,
  sortBy = 'created_at',
  sortOrder = 'desc',
  statuses = undefined,
  search = undefined
) => {
  try {
    const params = { page, limit, sort_by: sortBy, sort_order: sortOrder }

    // Adicionar filtros se fornecidos
    if (statuses && Array.isArray(statuses) && statuses.length > 0) {
      params.status = statuses.join(',')
    }

    if (search && search.trim()) {
      params.search = search
    }

    const response = await api.get('/contratos', { params })
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar contratos')
  }
}

/**
 * Buscar resultado de um contrato específico
 * @param {string} contratoId - ID do contrato
 * @returns {Promise} Dados do contrato com resultado
 */
export const fetchContratoResult = async (contratoId) => {
  try {
    const response = await api.get(`/contratos/${contratoId}`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao buscar resultado')
  }
}

/**
 * Deletar um contrato
 * @param {string} contratoId - ID do contrato
 * @returns {Promise} Confirmação de deleção
 */
export const deleteContrato = async (contratoId) => {
  try {
    const response = await api.delete(`/contratos/${contratoId}`)
    return response.data
  } catch (error) {
    throw new Error(error.message || 'Erro ao deletar contrato')
  }
}

/**
 * Set tokens after login
 */
export function setTokens(accessToken, refreshToken, user = null) {
  localStorage.setItem('access_token', accessToken)
  localStorage.setItem('refresh_token', refreshToken)
  if (user) {
    localStorage.setItem('user', JSON.stringify(user))
  }
  
  if (accessToken) {
    api.defaults.headers.common.Authorization = `Bearer ${accessToken}`
  }
}

/**
 * Clear all tokens
 */
export function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  
  if (api.defaults.headers.common.Authorization) {
    delete api.defaults.headers.common.Authorization
  }
}

/**
 * Get stored user info
 */
export function getUser() {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

/**
 * Get access token
 */
export function getAccessToken() {
  return localStorage.getItem('access_token')
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
  return !!localStorage.getItem('access_token')
}

export default api
