import styles from './Statistics.module.css'

function Statistics({
  pagesAnalyzed = 15,
  dataExtracted = 342,
  entitiesFound = 28,
  accuracy = 96.8,
  processingTime = '2m 34s',
  fileSize = '2.4 MB',
  timestamps = {
    started: '2024-02-03T14:28:00Z',
    completed: '2024-02-03T14:30:34Z'
  }
}) {
  const stats = [
    {
      icon: '📄',
      label: 'Páginas Analisadas',
      value: pagesAnalyzed,
      unit: 'págs',
      color: 'blue'
    },
    {
      icon: '📊',
      label: 'Dados Extraídos',
      value: dataExtracted,
      unit: 'campos',
      color: 'green'
    },
    {
      icon: '🏷️',
      label: 'Entidades Detectadas',
      value: entitiesFound,
      unit: 'entidades',
      color: 'purple'
    },
    {
      icon: '🎯',
      label: 'Precisão',
      value: accuracy.toFixed(1),
      unit: '%',
      color: 'orange'
    },
    {
      icon: '⏱️',
      label: 'Tempo Total',
      value: processingTime,
      unit: '',
      color: 'red'
    },
    {
      icon: '💾',
      label: 'Tamanho Arquivo',
      value: fileSize,
      unit: '',
      color: 'gray'
    },
  ]

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>📊 Estatísticas da Análise</h3>
      
      <div className={styles.grid}>
        {stats.map((stat, idx) => (
          <div 
            key={idx} 
            className={`${styles.statCard} ${styles[`stat${stat.color}`]}`}
          >
            <div className={styles.statIcon}>{stat.icon}</div>
            <div className={styles.statContent}>
              <div className={styles.statValue}>
                {stat.value}
                {stat.unit && <span className={styles.statUnit}>{stat.unit}</span>}
              </div>
              <div className={styles.statLabel}>{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Detailed Timestamps */}
      <div className={styles.timestamps}>
        <div className={styles.timestampItem}>
          <span className={styles.timestampLabel}>Início:</span>
          <span className={styles.timestampValue}>
            {new Date(timestamps.started).toLocaleString('pt-BR')}
          </span>
        </div>
        <div className={styles.timestampItem}>
          <span className={styles.timestampLabel}>Conclusão:</span>
          <span className={styles.timestampValue}>
            {new Date(timestamps.completed).toLocaleString('pt-BR')}
          </span>
        </div>
        <div className={styles.timestampItem}>
          <span className={styles.timestampLabel}>Duração:</span>
          <span className={styles.timestampValue}>{processingTime}</span>
        </div>
      </div>
    </div>
  )
}

export default Statistics
