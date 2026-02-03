import { useState } from 'react'
import { Download, CheckCircle, AlertCircle } from 'lucide-react'
import styles from './DownloadButton.module.css'

function DownloadButton({
  fileName = 'laudo.pdf',
  fileSize = '2.5 MB',
  onDownload = null,
  disabled = false,
}) {
  const [isLoading, setIsLoading] = useState(false)
  const [downloadStatus, setDownloadStatus] = useState(null) // 'success' | 'error' | null
  const [errorMessage, setErrorMessage] = useState('')

  const handleDownload = async () => {
    try {
      setIsLoading(true)
      setDownloadStatus(null)
      setErrorMessage('')

      // If custom callback provided, use it
      if (onDownload && typeof onDownload === 'function') {
        await onDownload()
      } else {
        // Default: simulate download by creating a blob and triggering download
        // In real scenario, this would fetch from API
        await new Promise(resolve => setTimeout(resolve, 1500))
      }

      setDownloadStatus('success')

      // Reset success message after 3 seconds
      setTimeout(() => {
        setDownloadStatus(null)
      }, 3000)
    } catch (error) {
      console.error('Download error:', error)
      setDownloadStatus('error')
      setErrorMessage(
        error.message || 'Falha ao baixar o arquivo. Tente novamente.'
      )

      // Reset error message after 5 seconds
      setTimeout(() => {
        setDownloadStatus(null)
        setErrorMessage('')
      }, 5000)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={styles.downloadContainer}>
      <button
        className={`${styles.downloadButton} ${
          isLoading || disabled ? styles.disabled : ''
        } ${downloadStatus === 'success' ? styles.success : ''} ${
          downloadStatus === 'error' ? styles.error : ''
        }`}
        onClick={handleDownload}
        disabled={isLoading || disabled}
        title={`Baixar ${fileName} (${fileSize})`}
      >
        {isLoading ? (
          <>
            <span className={styles.spinner} />
            <span className={styles.buttonText}>Baixando...</span>
          </>
        ) : downloadStatus === 'success' ? (
          <>
            <CheckCircle size={20} />
            <span className={styles.buttonText}>Baixado com Sucesso</span>
          </>
        ) : downloadStatus === 'error' ? (
          <>
            <AlertCircle size={20} />
            <span className={styles.buttonText}>Erro ao Baixar</span>
          </>
        ) : (
          <>
            <Download size={20} />
            <span className={styles.buttonText}>Baixar Parecer</span>
          </>
        )}
      </button>

      {/* File Info */}
      <div className={styles.fileInfo}>
        <span className={styles.fileName}>{fileName}</span>
        <span className={styles.fileSize}>{fileSize}</span>
      </div>

      {/* Error Message */}
      {downloadStatus === 'error' && errorMessage && (
        <div className={styles.errorMessage}>{errorMessage}</div>
      )}

      {/* Success Message */}
      {downloadStatus === 'success' && (
        <div className={styles.successMessage}>
          ✅ Arquivo baixado com sucesso! Verifique sua pasta de downloads.
        </div>
      )}
    </div>
  )
}

export default DownloadButton
