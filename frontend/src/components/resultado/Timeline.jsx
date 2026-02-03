import styles from './Timeline.module.css'

function Timeline({
  steps = [
    { id: 1, label: 'Enviado', status: 'completed', time: '14:28:00' },
    { id: 2, label: 'Validação', status: 'completed', time: '14:28:15' },
    { id: 3, label: 'Análise', status: 'completed', time: '14:28:45' },
    { id: 4, label: 'Geolocalização', status: 'completed', time: '14:30:00' },
    { id: 5, label: 'Parecer', status: 'completed', time: '14:30:30' },
    { id: 6, label: 'Finalizado', status: 'completed', time: '14:30:34' },
  ]
}) {
  const getStepIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✅'
      case 'processing':
        return '⏳'
      case 'failed':
        return '❌'
      default:
        return '○'
    }
  }

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>📈 Timeline de Processamento</h3>
      
      <div className={styles.timeline}>
        {steps.map((step, idx) => (
          <div key={step.id} className={styles.timelineWrapper}>
            {/* Step */}
            <div className={`${styles.step} ${styles[`step${step.status}`]}`}>
              <div className={styles.stepIcon}>
                {getStepIcon(step.status)}
              </div>
              <div className={styles.stepContent}>
                <div className={styles.stepLabel}>{step.label}</div>
                <div className={styles.stepTime}>{step.time}</div>
              </div>
            </div>

            {/* Connector */}
            {idx < steps.length - 1 && (
              <div className={`${styles.connector} ${styles[`connector${step.status}`]}`} />
            )}
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className={styles.summary}>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>Total de Etapas:</span>
          <span className={styles.summaryValue}>{steps.length}</span>
        </div>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>Etapas Concluídas:</span>
          <span className={styles.summaryValue}>
            {steps.filter(s => s.status === 'completed').length}
          </span>
        </div>
        <div className={styles.summaryItem}>
          <span className={styles.summaryLabel}>Duração Total:</span>
          <span className={styles.summaryValue}>
            {steps[steps.length - 1]?.time || '--'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default Timeline
