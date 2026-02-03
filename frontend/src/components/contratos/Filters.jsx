import styles from './Filters.module.css'

function Filters({ 
  selectedStatuses = [], 
  onStatusChange = () => {},
  statuses = ['pendente', 'processando', 'concluído', 'erro']
}) {
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'pendente':
        return { emoji: '⏳', label: 'Pendente' }
      case 'processando':
        return { emoji: '⚙️', label: 'Processando' }
      case 'concluído':
      case 'concluido':
        return { emoji: '✅', label: 'Concluído' }
      case 'erro':
        return { emoji: '❌', label: 'Erro' }
      default:
        return { emoji: '❓', label: 'Desconhecido' }
    }
  }

  const handleStatusToggle = (status) => {
    if (selectedStatuses.includes(status)) {
      onStatusChange(selectedStatuses.filter(s => s !== status))
    } else {
      onStatusChange([...selectedStatuses, status])
    }
  }

  const handleClearFilters = () => {
    onStatusChange([])
  }

  return (
    <div className={styles.filtersContainer}>
      <div className={styles.header}>
        <h3 className={styles.title}>🔍 Filtrar por Status</h3>
        {selectedStatuses.length > 0 && (
          <button 
            className={styles.clearBtn}
            onClick={handleClearFilters}
          >
            Limpar filtros
          </button>
        )}
      </div>

      <div className={styles.statusButtons}>
        {statuses.map((status) => {
          const isSelected = selectedStatuses.includes(status)
          const { emoji, label } = getStatusColor(status)

          return (
            <button
              key={status}
              className={`${styles.statusBtn} ${isSelected ? styles.selected : ''}`}
              onClick={() => handleStatusToggle(status)}
            >
              <span className={styles.emoji}>{emoji}</span>
              <span className={styles.label}>{label}</span>
              {isSelected && <span className={styles.checkmark}>✓</span>}
            </button>
          )
        })}
      </div>

      {selectedStatuses.length > 0 && (
        <div className={styles.selectedInfo}>
          <p>Mostrando {selectedStatuses.length} filtro(s) ativo(s)</p>
        </div>
      )}
    </div>
  )
}

export default Filters
