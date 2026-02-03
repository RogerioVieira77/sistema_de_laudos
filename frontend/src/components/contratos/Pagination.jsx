import { ChevronLeft, ChevronRight } from 'lucide-react'
import styles from './Pagination.module.css'

function Pagination({ 
  currentPage = 1, 
  totalPages = 1, 
  totalItems = 0,
  itemsPerPage = 10,
  onPageChange = () => {},
  onItemsPerPageChange = () => {}
}) {
  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1)
    }
  }

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1)
    }
  }

  const handlePageInput = (page) => {
    const pageNum = parseInt(page)
    if (pageNum >= 1 && pageNum <= totalPages) {
      onPageChange(pageNum)
    }
  }

  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, totalItems)

  return (
    <div className={styles.paginationContainer}>
      <div className={styles.info}>
        <span className={styles.itemsInfo}>
          Mostrando <strong>{startItem}</strong> a <strong>{endItem}</strong> de <strong>{totalItems}</strong> itens
        </span>
      </div>

      <div className={styles.controls}>
        <div className={styles.itemsPerPage}>
          <label htmlFor="itemsPerPage">Por página:</label>
          <select
            id="itemsPerPage"
            value={itemsPerPage}
            onChange={(e) => onItemsPerPageChange(parseInt(e.target.value))}
            className={styles.select}
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>

        <div className={styles.pageControls}>
          <button
            className={styles.navBtn}
            onClick={handlePrevious}
            disabled={currentPage === 1}
            title="Página anterior"
          >
            <ChevronLeft size={18} />
          </button>

          <div className={styles.pageInfo}>
            <input
              type="number"
              min="1"
              max={totalPages}
              value={currentPage}
              onChange={(e) => handlePageInput(e.target.value)}
              className={styles.pageInput}
            />
            <span>de {totalPages}</span>
          </div>

          <button
            className={styles.navBtn}
            onClick={handleNext}
            disabled={currentPage === totalPages || totalPages === 0}
            title="Próxima página"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default Pagination
