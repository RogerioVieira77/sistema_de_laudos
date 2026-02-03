import React from 'react'
import styles from './ErrorBoundary.module.css'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    })
    // You can also log the error to an error reporting service here
    console.error('Error caught by boundary:', error, errorInfo)
  }

  resetError = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className={styles.errorBoundaryContainer}>
          <div className={styles.content}>
            <h1 className={styles.title}>Oops! Algo deu errado</h1>
            <p className={styles.description}>
              Desculpe, ocorreu um erro inesperado na aplicação.
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className={styles.details}>
                <summary className={styles.summary}>Detalhes do Erro (Dev Only)</summary>
                <pre className={styles.errorStack}>
                  {this.state.error.toString()}
                  {'\n\n'}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}

            <div className={styles.actions}>
              <button
                className={styles.primaryButton}
                onClick={this.resetError}
              >
                Tentar Novamente
              </button>
              <button
                className={styles.secondaryButton}
                onClick={() => (window.location.href = '/')}
              >
                Voltar para Home
              </button>
            </div>
          </div>
          <div className={styles.illustration}>
            <div className={styles.icon}>⚠️</div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
