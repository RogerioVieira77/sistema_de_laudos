import { useState } from 'react'
import { Menu, X, User, Bell, LogOut, LogIn } from 'lucide-react'
import { useAuth, useUser } from '../../contexts/AuthContext'
import styles from './Navbar.module.css'

export default function Navbar({ onMenuClick }) {
  const [showUserMenu, setShowUserMenu] = useState(false)
  const { isAuthenticated, login, logout } = useAuth()
  const user = useUser()

  return (
    <nav className={styles.navbar}>
      <div className={styles.navContainer}>
        {/* Logo/Titulo */}
        <div className={styles.logoSection}>
          <button 
            className={styles.menuToggle}
            onClick={onMenuClick}
            aria-label="Toggle menu"
          >
            <Menu size={24} />
          </button>
          <h1 className={styles.logo}>Sistema de Laudos</h1>
        </div>

        {/* Menu Central - Desktop only */}
        {isAuthenticated && (
          <div className={styles.navMenu}>
            <a href="/" className={styles.navLink}>Home</a>
            <a href="/upload" className={styles.navLink}>Upload</a>
            <a href="/contratos" className={styles.navLink}>Contratos</a>
            <a href="/sobre" className={styles.navLink}>Sobre</a>
          </div>
        )}

        {/* Icons */}
        <div className={styles.rightSection}>
          {isAuthenticated ? (
            <>
              {/* Notificações */}
              <button className={styles.iconButton} aria-label="Notifications">
                <Bell size={20} />
                <span className={styles.notificationBadge}>3</span>
              </button>

              {/* User Menu */}
              <div className={styles.userMenuContainer}>
                <button 
                  className={styles.iconButton}
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  aria-label="User menu"
                  title={user?.email}
                >
                  <User size={20} />
                </button>

                {showUserMenu && (
                  <div className={styles.userDropdown}>
                    <div className={styles.userInfo}>
                      <div className={styles.userName}>{user?.name}</div>
                      <div className={styles.userEmail}>{user?.email}</div>
                    </div>
                    <hr className={styles.divider} />
                    <a href="/profile" className={styles.dropdownItem}>Perfil</a>
                    <a href="/settings" className={styles.dropdownItem}>Configurações</a>
                    <hr className={styles.divider} />
                    <button 
                      onClick={() => {
                        setShowUserMenu(false)
                        logout()
                      }}
                      className={styles.dropdownItem + ' ' + styles.logout}
                    >
                      <LogOut size={16} />
                      Sair
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            /* Login Button */
            <button 
              onClick={login}
              className={styles.loginBtn}
            >
              <LogIn size={20} />
              Entrar
            </button>
          )}
        </div>
      </div>
    </nav>
  )
}
