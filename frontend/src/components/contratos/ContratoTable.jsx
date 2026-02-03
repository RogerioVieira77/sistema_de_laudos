import { ChevronUp, ChevronDown, Eye, Download, Trash2 } from 'lucide-react'
import styles from './ContratoTable.module.css'

function ContratoTable({ 
  contratos = [], 
  loading = false, 
  sortBy = null, 
  sortOrder = 'asc',
  onSort = () => {},
  onView = () => {},
  onDownload = () => {},
  onDelete = () => {}
}) {
  const getStatusBadgeClass = (status) => {
    switch (status?.toLowerCase()) {
      case 'pendente':
        return styles.statusPendente
      case 'processando':
        return styles.statusProcessando
      case 'concluído':
      case 'concluido':
        return styles.statusConcluido
      case 'erro':
        return styles.statusErro
      default:
        return styles.statusPendente
    }
  }

  const getStatusLabel = (status) => {
    switch (status?.toLowerCase()) {
      case 'pendente':
        return '⏳ Pendente'
      case 'processando':
        return '⚙️ Processando'
      case 'concluído':
      case 'concluido':
        return '✅ Concluído'
      case 'erro':
        return '❌ Erro'
      default:
        return '❓ Desconhecido'
    }
  }

  const SortIcon = ({ column }) => {
    if (sortBy !== column) return <ChevronUp size={16} className={styles.sortIconInactive} />
    return sortOrder === 'asc' ? 
      <ChevronUp size={16} className={styles.sortIconActive} /> : 
      <ChevronDown size={16} className={styles.sortIconActive} />
  }

  const formatDate = (date) => {
    if (!date) return '-'
    return new Date(date).toLocaleDateString('pt-BR')
  }

  return (
    <div className={styles.tableContainer}>
      {loading ? (
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>Carregando contratos...</p>
        </div>
      ) : contratos.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>📋</div>
          <h3>Nenhum contrato encontrado</h3>
          <p>Envie um arquivo PDF para começar</p>
        </div>
      ) : (
        <table className={styles.table}>
          <thead>
            <tr>
              <th 
                onClick={() => onSort('id')}
                className={styles.sortable}
              >
                <span>ID</span>
                <SortIcon column="id" />
              </th>
              <th 
                onClick={() => onSort('filename')}
                className={styles.sortable}
              >
                <span>Arquivo</span>
                <SortIcon column="filename" />
              </th>
              <th 
                onClick={() => onSort('created_at')}
                className={styles.sortable}
              >
                <span>Data Envio</span>
                <SortIcon column="created_at" />
              </th>
              <th 
                onClick={() => onSort('status')}
                className={styles.sortable}
              >
                <span>Status</span>
                <SortIcon column="status" />
              </th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {contratos.map((contrato) => (
              <tr key={contrato.id} className={styles.tableRow}>
                <td className={styles.idCell}>
                  <code>{contrato.id?.substring(0, 8)}...</code>
                </td>
                <td className={styles.filenameCell}>
                  <div className={styles.fileInfo}>
                    <span className={styles.fileIcon}>📄</span>
                    <div>
                      <div className={styles.filename}>{contrato.filename || 'Sem nome'}</div>
                      <div className={styles.fileSize}>
                        {contrato.file_size ? `${(contrato.file_size / 1024).toFixed(1)} KB` : '-'}
                      </div>
                    </div>
                  </div>
                </td>
                <td className={styles.dateCell}>
                  {formatDate(contrato.created_at)}
                </td>
                <td className={styles.statusCell}>
                  <span className={`${styles.statusBadge} ${getStatusBadgeClass(contrato.status)}`}>
                    {getStatusLabel(contrato.status)}
                  </span>
                </td>
                <td className={styles.actionsCell}>
                  <div className={styles.actionButtons}>
                    <button
                      className={styles.actionBtn}
                      title="Ver detalhes"
                      onClick={() => onView(contrato.id)}
                    >
                      <Eye size={18} />
                    </button>
                    {contrato.status?.toLowerCase() === 'concluído' || contrato.status?.toLowerCase() === 'concluido' ? (
                      <button
                        className={styles.actionBtn}
                        title="Baixar resultado"
                        onClick={() => onDownload(contrato.id)}
                      >
                        <Download size={18} />
                      </button>
                    ) : null}
                    <button
                      className={`${styles.actionBtn} ${styles.deleteBtn}`}
                      title="Deletar"
                      onClick={() => onDelete(contrato.id)}
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default ContratoTable
