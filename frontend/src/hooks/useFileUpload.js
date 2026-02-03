import { useState, useCallback } from 'react'
import { uploadContract } from '../services/contractService'
import useAppStore from '../store/appStore'

/**
 * Hook customizado para gerenciar upload de arquivos
 * @returns {Object} Estado e funções de controle do upload
 */
export const useFileUpload = () => {
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState(null) // null, 'uploading', 'completed', 'error'
  const [message, setMessage] = useState('')
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  /**
   * Inicia o upload do arquivo
   */
  const handleUpload = useCallback(async (selectedFile) => {
    if (!selectedFile) {
      setError('Nenhum arquivo selecionado')
      return
    }

    try {
      setIsLoading(true)
      setStatus('uploading')
      setProgress(0)
      setMessage('Preparando envio...')
      setError(null)
      setResult(null)

      const response = await uploadContract(selectedFile, (percentProgress) => {
        setProgress(percentProgress)
        
        if (percentProgress < 30) {
          setMessage('Conectando ao servidor...')
        } else if (percentProgress < 60) {
          setMessage('Enviando arquivo...')
        } else if (percentProgress < 90) {
          setMessage('Processando arquivo no servidor...')
        } else {
          setMessage('Finalizando...')
        }
      })

      setProgress(100)
      setStatus('completed')
      setMessage('Arquivo enviado com sucesso!')
      setResult(response)
      setFile(null)

      // Show success notification
      useAppStore.getState().showSuccess('Contrato enviado com sucesso! Análise iniciada.')

      // Limpar resultado após 5 segundos
      setTimeout(() => {
        setStatus(null)
        setMessage('')
        setProgress(0)
      }, 5000)
    } catch (err) {
      setStatus('error')
      setError(err.message)
      setMessage(err.message)
      setProgress(0)

      // Show error notification
      useAppStore.getState().showError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Reseta o estado do upload
   */
  const resetUpload = useCallback(() => {
    setFile(null)
    setProgress(0)
    setStatus(null)
    setMessage('')
    setError(null)
    setResult(null)
  }, [])

  /**
   * Seleciona um arquivo
   */
  const selectFile = useCallback((selectedFile) => {
    setFile(selectedFile)
  }, [])

  return {
    file,
    progress,
    status,
    message,
    error,
    result,
    isLoading,
    handleUpload,
    resetUpload,
    selectFile,
  }
}

export default useFileUpload
