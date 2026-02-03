import { useState, useEffect } from 'react'
import { Search, X } from 'lucide-react'
import styles from './SearchBox.module.css'

function SearchBox({ 
  value = '', 
  placeholder = 'Buscar por nome ou ID...',
  onSearch = () => {},
  debounceDelay = 300,
  loading = false
}) {
  const [inputValue, setInputValue] = useState(value)
  const [debounceTimer, setDebounceTimer] = useState(null)

  useEffect(() => {
    // Clear existing timer
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }

    // Set new timer
    const timer = setTimeout(() => {
      onSearch(inputValue)
    }, debounceDelay)

    setDebounceTimer(timer)

    // Cleanup
    return () => clearTimeout(timer)
  }, [inputValue, debounceDelay, onSearch])

  const handleChange = (e) => {
    setInputValue(e.target.value)
  }

  const handleClear = () => {
    setInputValue('')
    onSearch('')
  }

  return (
    <div className={styles.searchBoxContainer}>
      <div className={styles.searchInput}>
        <Search size={20} className={styles.searchIcon} />
        <input
          type="text"
          value={inputValue}
          onChange={handleChange}
          placeholder={placeholder}
          className={styles.input}
          disabled={loading}
        />
        {inputValue && (
          <button
            className={styles.clearBtn}
            onClick={handleClear}
            title="Limpar busca"
            disabled={loading}
          >
            <X size={18} />
          </button>
        )}
      </div>
      {loading && <div className={styles.loadingDot} />}
    </div>
  )
}

export default SearchBox
