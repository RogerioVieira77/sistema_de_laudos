import { useState } from 'react'
import { Home, Upload, FileText, MapPin, CheckCircle, Settings, LogOut } from 'lucide-react'
import styles from './Sidebar.module.css'

const menuItems = [
  { id: 'home', label: 'Home', icon: Home, href: '/' },
  { id: 'upload', label: 'Upload', icon: Upload, href: '/upload' },
  { id: 'contratos', label: 'Contratos', icon: FileText, href: '/contratos' },
  { id: 'mapa', label: 'Mapa', icon: MapPin, href: '/map' },
  { id: 'resultados', label: 'Resultados', icon: CheckCircle, href: '/contratos' },
]

const bottomItems = [
  { id: 'settings', label: 'Configurações', icon: Settings, href: '/settings' },
  { id: 'logout', label: 'Sair', icon: LogOut, href: '/logout' },
]

export default function Sidebar({ isOpen, onClose, activeItem = 'home' }) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <>
      {/* Overlay mobile */}
      {isOpen && <div className={styles.overlay} onClick={onClose} />}

      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${isOpen ? styles.open : ''} ${collapsed ? styles.collapsed : ''}`}>
        {/* Header com toggle */}
        <div className={styles.sidebarHeader}>
          <h2 className={styles.title}>Menu</h2>
        </div>

        {/* Menu Items Principal */}
        <nav className={styles.navSection}>
          <div className={styles.menuItems}>
            {menuItems.map(item => {
              const Icon = item.icon
              return (
                <a
                  key={item.id}
                  href={item.href}
                  className={`${styles.menuItem} ${activeItem === item.id ? styles.active : ''}`}
                  title={item.label}
                >
                  <Icon size={20} className={styles.icon} />
                  <span className={styles.label}>{item.label}</span>
                </a>
              )
            })}
          </div>
        </nav>

        {/* Menu Items Bottom */}
        <div className={styles.bottomSection}>
          <div className={styles.menuItems}>
            {bottomItems.map(item => {
              const Icon = item.icon
              return (
                <a
                  key={item.id}
                  href={item.href}
                  className={`${styles.menuItem} ${item.id === 'logout' ? styles.logout : ''}`}
                  title={item.label}
                >
                  <Icon size={20} className={styles.icon} />
                  <span className={styles.label}>{item.label}</span>
                </a>
              )
            })}
          </div>
        </div>

        {/* Toggle Collapse Button */}
        <button 
          className={styles.collapseBtn}
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? 'Expandir' : 'Recolher'}
        >
          {collapsed ? '→' : '←'}
        </button>
      </aside>
    </>
  )
}
