import { useEffect } from 'react'
import { AlertCircle, CheckCircle, InfoIcon, AlertTriangle, X } from 'lucide-react'
import useAppStore from '../store/appStore'
import styles from './Notifications.module.css'

function Notifications() {
  const notifications = useAppStore((state) => state.notifications)
  const removeNotification = useAppStore((state) => state.removeNotification)

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle size={20} />
      case 'error':
        return <AlertCircle size={20} />
      case 'warning':
        return <AlertTriangle size={20} />
      case 'info':
        return <InfoIcon size={20} />
      default:
        return null
    }
  }

  return (
    <div className={styles.container}>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`${styles.notification} ${styles[notification.type]}`}
        >
          <div className={styles.content}>
            <div className={styles.icon}>{getIcon(notification.type)}</div>
            <p className={styles.message}>{notification.message}</p>
          </div>
          <button
            className={styles.closeButton}
            onClick={() => removeNotification(notification.id)}
            aria-label="Fechar notificação"
          >
            <X size={18} />
          </button>
        </div>
      ))}
    </div>
  )
}

export default Notifications
