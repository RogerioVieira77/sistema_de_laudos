import { useState } from 'react'
import { Upload, AlertCircle, CheckCircle, Loader } from 'lucide-react'
import styles from './UploadArea.module.css'

function UploadArea({ onFileSelect, disabled = false }) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [error, setError] = useState(null)

  const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
  const ALLOWED_TYPES = ['application/pdf']

  const validateFile = (file) => {
    // Validar tipo
    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('❌ Apenas arquivos PDF são aceitos')
      return false
    }

    // Validar tamanho
    if (file.size > MAX_FILE_SIZE) {
      setError(`❌ Arquivo muito grande. Máximo: 10MB (seu arquivo: ${(file.size / 1024 / 1024).toFixed(2)}MB)`)
      return false
    }

    setError(null)
    return true
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragOver(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (validateFile(file)) {
        setSelectedFile(file)
        onFileSelect(file)
      }
    }
  }

  const handleFileInput = (e) => {
    const file = e.target.files?.[0]
    if (file && validateFile(file)) {
      setSelectedFile(file)
      onFileSelect(file)
    }
  }

  const handleClearFile = () => {
    setSelectedFile(null)
    setError(null)
  }

  return (
    <div className={styles.uploadAreaContainer}>
      {!selectedFile ? (
        <>
          <div
            className={`${styles.dropZone} ${isDragOver ? styles.dragOver : ''} ${disabled ? styles.disabled : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload size={48} className={styles.uploadIcon} />
            <h3 className={styles.title}>Arraste um arquivo PDF aqui</h3>
            <p className={styles.subtitle}>ou clique para selecionar do seu computador</p>
            <p className={styles.hint}>Tamanho máximo: 10MB</p>

            <input
              type="file"
              accept=".pdf"
              onChange={handleFileInput}
              className={styles.fileInput}
              disabled={disabled}
              id="fileInput"
            />
            <label htmlFor="fileInput" className={styles.browseButton}>
              Procurar Arquivo
            </label>
          </div>

          {error && (
            <div className={styles.errorMessage}>
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}
        </>
      ) : (
        <div className={styles.fileSelected}>
          <div className={styles.filePreview}>
            <CheckCircle size={40} className={styles.checkIcon} />
            <div className={styles.fileInfo}>
              <h3 className={styles.fileName}>{selectedFile.name}</h3>
              <p className={styles.fileSize}>
                {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          </div>

          <button
            className={styles.clearButton}
            onClick={handleClearFile}
            disabled={disabled}
          >
            ✕ Remover arquivo
          </button>
        </div>
      )}
    </div>
  )
}

export default UploadArea
