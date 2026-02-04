import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import { LogIn, LogOut } from 'lucide-react'
import styles from './Login.module.css'

/**
 * Login Component
 * Shows login/logout button and user info
 */
export const Login = () => {
  const { user, isAuthenticated, isLoading, login, logout, error } = useAuth()

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.skeleton}>Carregando...</div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      {error && <div className={styles.error}>{error}</div>}

      {isAuthenticated && user ? (
        <div className={styles.userInfo}>
          <div className={styles.user}>
            <span className={styles.email}>{user.profile?.email}</span>
            <span className={styles.name}>{user.profile?.name}</span>
          </div>
          <button onClick={logout} className={styles.logoutBtn}>
            <LogOut size={18} />
            Sair
          </button>
        </div>
      ) : (
        <button onClick={login} className={styles.loginBtn}>
          <LogIn size={18} />
          Entrar
        </button>
      )}
    </div>
  )
}

/**
 * LoginPage Component
 * Full page login redirect
 */
export const LoginPage = () => {
  const { isLoading, login, error } = useAuth()

  React.useEffect(() => {
    if (!isLoading && !error) {
      login()
    }
  }, [isLoading, error, login])

  return (
    <div className={styles.loginPageContainer}>
      <div className={styles.loginPageContent}>
        <h1>Sistema de Laudos</h1>
        <p>Redirecionando para login...</p>
        {error && <div className={styles.error}>{error}</div>}
      </div>
    </div>
  )
}

export default Login
