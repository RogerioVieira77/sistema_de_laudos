import { CheckCircle, AlertCircle, Loader } from 'lucide-react'
import styles from './ProgressBar.module.css'

function ProgressBar({ progress, status, message }) {
  const getStatusColor = () => {
    switch (status) {
      case 'uploading':
        return styles.uploading
      case 'completed':
        return styles.completed
      case 'error':
        return styles.error
      default:
        return ''
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'uploading':
        return <Loader size={24} className={styles.spinner} />
      case 'completed':
        return <CheckCircle size={24} className={styles.icon} />
      case 'error':
        return <AlertCircle size={24} className={styles.icon} />
      default:
        return null
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'uploading':
        return 'Enviando...'
      case 'completed':
        return 'Envio concluído!'
      case 'error':
        return 'Erro no envio'
      default:
        return ''
    }
  }

  return (
    <div className={`${styles.progressContainer} ${getStatusColor()}`}>
      <div className={styles.header}>
        <div className={styles.statusInfo}>
          {getStatusIcon()}
          <div>
            <h4 className={styles.statusTitle}>{getStatusText()}</h4>
            {message && <p className={styles.message}>{message}</p>}
          </div>
        </div>
        <span className={styles.percentage}>{progress}%</span>
      </div>

      <div className={styles.barContainer}>
        <div
          className={styles.progressBar}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}

export default ProgressBar
