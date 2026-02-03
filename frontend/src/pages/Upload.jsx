import { useState } from 'react'
import MainLayout from '../components/layouts/MainLayout'
import UploadArea from '../components/upload/UploadArea'
import ProgressBar from '../components/upload/ProgressBar'
import { useFileUpload } from '../hooks/useFileUpload'
import styles from './Upload.module.css'

function Upload() {
  const {
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
  } = useFileUpload()

  const handleFileSelect = (selectedFile) => {
    selectFile(selectedFile)
  }

  const handleSubmit = async () => {
    await handleUpload(file)
  }

  const handleReset = () => {
    resetUpload()
  }

  return (
    <MainLayout activeItem="upload">
      <div className={styles.uploadContainer}>
        {/* Header */}
        <div className={styles.header}>
          <h1 className={styles.title}>Enviar Contrato</h1>
          <p className={styles.description}>
            Carregue um arquivo PDF para que o sistema analise o contrato e gere um parecer automático.
          </p>
        </div>

        {/* Main Content */}
        <div className={styles.content}>
          <div className={styles.leftColumn}>
            {/* Upload Area */}
            <UploadArea
              onFileSelect={handleFileSelect}
              disabled={isLoading}
            />

            {/* Progress Bar */}
            {status && (
              <ProgressBar
                progress={progress}
                status={status}
                message={message}
              />
            )}

            {/* Error Message */}
            {error && !status && (
              <div className={styles.errorAlert}>
                <span className={styles.errorIcon}>⚠️</span>
                <span>{error}</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className={styles.actions}>
              <button
                className={styles.uploadButton}
                onClick={handleSubmit}
                disabled={!file || isLoading || status === 'completed'}
              >
                {isLoading ? 'Enviando...' : 'Enviar Arquivo'}
              </button>

              {status === 'completed' && (
                <button
                  className={styles.resetButton}
                  onClick={handleReset}
                >
                  Enviar Outro Arquivo
                </button>
              )}
            </div>
          </div>

          {/* Right Column - Info */}
          <div className={styles.rightColumn}>
            <div className={styles.infoCard}>
              <h3 className={styles.infoTitle}>📋 Formatos Aceitos</h3>
              <ul className={styles.infoList}>
                <li>✓ PDF (.pdf)</li>
                <li>✗ Word, Excel</li>
                <li>✗ Imagens</li>
              </ul>
            </div>

            <div className={styles.infoCard}>
              <h3 className={styles.infoTitle}>📏 Tamanho do Arquivo</h3>
              <p className={styles.infoText}>Máximo: <strong>10MB</strong></p>
              <p className={styles.infoSubtext}>Certifique-se que o arquivo está em boa qualidade</p>
            </div>

            <div className={styles.infoCard}>
              <h3 className={styles.infoTitle}>⏱️ Tempo de Processamento</h3>
              <p className={styles.infoText}>
                Contratos são analisados em <strong>segundos a minutos</strong>
              </p>
              <p className={styles.infoSubtext}>
                Você será notificado quando o resultado estiver pronto
              </p>
            </div>

            <div className={styles.infoCard}>
              <h3 className={styles.infoTitle}>🔒 Segurança</h3>
              <p className={styles.infoText}>
                Seus arquivos são <strong>criptografados</strong> e armazenados com segurança
              </p>
              <p className={styles.infoSubtext}>
                Não compartilhamos dados com terceiros
              </p>
            </div>
          </div>
        </div>

        {/* Success Card */}
        {status === 'completed' && result && (
          <div className={styles.successCard}>
            <div className={styles.successIcon}>✨</div>
            <h2>Upload Realizado com Sucesso!</h2>
            <p>Seu contrato foi recebido e está sendo processado pelo nosso sistema.</p>
            {result.id && (
              <div className={styles.resultInfo}>
                <p><strong>ID do Contrato:</strong> {result.id}</p>
                <p><strong>Status:</strong> {result.status || 'Processando...'}</p>
              </div>
            )}
            <p className={styles.nextSteps}>
              Você pode acompanhar o status do seu contrato na página <strong>Contratos</strong>
            </p>
          </div>
        )}
      </div>
    </MainLayout>
  )
}

export default Upload
