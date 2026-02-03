import { useState } from 'react'
import Navbar from '../navbar/Navbar'
import Sidebar from '../sidebar/Sidebar'
import Footer from '../footer/Footer'
import styles from './MainLayout.module.css'

export default function MainLayout({ children, activeItem = 'home' }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleMenuClick = () => {
    setSidebarOpen(!sidebarOpen)
  }

  const handleCloseSidebar = () => {
    setSidebarOpen(false)
  }

  return (
    <div className={styles.layout}>
      {/* Navbar */}
      <Navbar onMenuClick={handleMenuClick} />

      {/* Container Principal */}
      <div className={styles.container}>
        {/* Sidebar */}
        <Sidebar 
          isOpen={sidebarOpen} 
          onClose={handleCloseSidebar}
          activeItem={activeItem}
        />

        {/* Main Content */}
        <main className={styles.main}>
          <div className={styles.content}>
            {children}
          </div>
          
          {/* Footer */}
          <Footer />
        </main>
      </div>
    </div>
  )
}
