import { useState, useEffect, useCallback } from 'react'
import { fetchContratos } from '../services/contractService'
import useAppStore from '../store/appStore'

export function useContratos() {
  const [contratos, setContratos] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(10)
  const [totalItems, setTotalItems] = useState(0)

  // Filtering & Sorting
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('desc')
  const [selectedStatuses, setSelectedStatuses] = useState([])
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch contratos with current filters
  const fetchContratosList = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetchContratos({
        page: currentPage,
        limit: itemsPerPage,
        sort_by: sortBy,
        sort_order: sortOrder,
        status: selectedStatuses.length > 0 ? selectedStatuses.join(',') : undefined,
        search: searchQuery || undefined,
      })

      if (response && response.data) {
        setContratos(Array.isArray(response.data) ? response.data : response.data.items || [])
        setTotalItems(response.total || response.data.length || 0)
      } else {
        setContratos([])
        setTotalItems(0)
      }
    } catch (err) {
      const errorMessage = err.message || 'Erro ao carregar contratos'
      setError(errorMessage)
      setContratos([])
      // Show error in app store
      useAppStore.getState().showError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [currentPage, itemsPerPage, sortBy, sortOrder, selectedStatuses, searchQuery])

  // Auto-fetch when dependencies change
  useEffect(() => {
    fetchContratosList()
  }, [fetchContratosList])

  // Reset to page 1 when filters/search changes
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1)
    }
  }, [selectedStatuses, searchQuery, sortBy, sortOrder])

  // Handle sorting
  const handleSort = useCallback((column) => {
    if (sortBy === column) {
      // Toggle sort order
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      // New column, default to asc
      setSortBy(column)
      setSortOrder('asc')
    }
  }, [sortBy, sortOrder])

  // Handle status filter
  const handleStatusChange = useCallback((statuses) => {
    setSelectedStatuses(statuses)
  }, [])

  // Handle search
  const handleSearch = useCallback((query) => {
    setSearchQuery(query)
  }, [])

  // Handle pagination
  const handlePageChange = useCallback((page) => {
    const maxPage = Math.ceil(totalItems / itemsPerPage)
    if (page >= 1 && page <= maxPage) {
      setCurrentPage(page)
      // Scroll to top of table
      const tableElement = document.getElementById('contratos-table')
      if (tableElement) {
        tableElement.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }, [totalItems, itemsPerPage])

  // Handle items per page change
  const handleItemsPerPageChange = useCallback((items) => {
    setItemsPerPage(items)
    setCurrentPage(1)
  }, [])

  // Calculate total pages
  const totalPages = Math.ceil(totalItems / itemsPerPage)

  return {
    // Data
    contratos,
    loading,
    error,

    // Pagination
    currentPage,
    itemsPerPage,
    totalItems,
    totalPages,

    // Sorting
    sortBy,
    sortOrder,

    // Filtering
    selectedStatuses,
    searchQuery,

    // Handlers
    handleSort,
    handleStatusChange,
    handleSearch,
    handlePageChange,
    handleItemsPerPageChange,

    // Manual refresh
    refresh: fetchContratosList,
  }
}
