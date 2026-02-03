import { useState } from 'react'
import MainLayout from '../components/layouts/MainLayout'
import ContratoTable from '../components/contratos/ContratoTable'
import Pagination from '../components/contratos/Pagination'
import Filters from '../components/contratos/Filters'
import SearchBox from '../components/contratos/SearchBox'
import { useContratos } from '../hooks/useContratos'
import styles from './Contratos.module.css'

function Contratos() {
  const {
    contratos,
    loading,
    error,
    currentPage,
    itemsPerPage,
    totalItems,
    totalPages,
    sortBy,
    sortOrder,
    selectedStatuses,
    searchQuery,
    handleSort,
    handleStatusChange,
    handleSearch,
    handlePageChange,
    handleItemsPerPageChange,
  } = useContratos()

  const [expandedFilters, setExpandedFilters] = useState(true)

  const handleDelete = (id) => {
    // Será implementado quando integrar com API de deleção
    console.log('Deletar contrato:', id)
  }

  const handleView = (id) => {
    // Redirecionar para página de detalhes
    console.log('Ver contrato:', id)
  }

  const handleDownload = (id, filename) => {
    // Será implementado quando integrar com API de download
    console.log('Baixar contrato:', id, filename)
  }

  return (
    <MainLayout activeItem="contratos">
      <div className={styles.page}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.titleSection}>
            <h1 className={styles.title}>📋 Meus Contratos</h1>
            <p className={styles.subtitle}>
              Gerencie seus contratos e acompanhe o status de análise
            </p>
          </div>
          <div className={styles.stats}>
            <div className={styles.statCard}>
              <span className={styles.statLabel}>Total</span>
              <span className={styles.statValue}>{totalItems}</span>
            </div>
            <div className={styles.statCard}>
              <span className={styles.statLabel}>Página</span>
              <span className={styles.statValue}>
                {currentPage}/{totalPages || 1}
              </span>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className={styles.errorMessage}>
            <span>❌ {error}</span>
          </div>
        )}

        {/* Search Bar */}
        <div className={styles.searchSection}>
          <SearchBox
            value={searchQuery}
            placeholder="Buscar por filename, ID ou informações..."
            onSearch={handleSearch}
            loading={loading}
            debounceDelay={300}
          />
        </div>

        {/* Filters Toggle for Mobile */}
        <button
          className={styles.filtersToggle}
          onClick={() => setExpandedFilters(!expandedFilters)}
        >
          🔍 Filtros {expandedFilters ? '−' : '+'}
        </button>

        {/* Main Content */}
        <div className={styles.container}>
          {/* Filters Sidebar */}
          {expandedFilters && (
            <aside className={styles.sidebar}>
              <Filters
                selectedStatuses={selectedStatuses}
                onStatusChange={handleStatusChange}
                statuses={['pendente', 'processando', 'concluído', 'erro']}
              />
            </aside>
          )}

          {/* Table Section */}
          <main className={styles.mainContent} id="contratos-table">
            {totalItems === 0 && !loading ? (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>📄</div>
                <h3>Nenhum contrato encontrado</h3>
                <p>
                  {searchQuery || selectedStatuses.length > 0
                    ? 'Tente alterar seus filtros de busca'
                    : 'Comece a enviar contratos para análise'}
                </p>
              </div>
            ) : (
              <>
                <ContratoTable
                  contratos={contratos}
                  loading={loading}
                  sortBy={sortBy}
                  sortOrder={sortOrder}
                  onSort={handleSort}
                  onView={handleView}
                  onDownload={handleDownload}
                  onDelete={handleDelete}
                />

                {totalPages > 1 && (
                  <div className={styles.paginationWrapper}>
                    <Pagination
                      currentPage={currentPage}
                      totalPages={totalPages}
                      totalItems={totalItems}
                      itemsPerPage={itemsPerPage}
                      onPageChange={handlePageChange}
                      onItemsPerPageChange={handleItemsPerPageChange}
                    />
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </div>
    </MainLayout>
  )
}

export default Contratos
