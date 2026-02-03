import { useNavigate } from 'react-router-dom'
import MainLayout from '../components/layouts/MainLayout'
import styles from './NotFound.module.css'

function NotFound() {
  const navigate = useNavigate()

  return (
    <MainLayout activeItem="home">
      <div className={styles.notFoundContainer}>
        <div className={styles.content}>
          <h1 className={styles.code}>404</h1>
          <h2 className={styles.title}>Página Não Encontrada</h2>
          <p className={styles.description}>
            Desculpe, a página que você está procurando não existe ou foi removida.
          </p>
          <button 
            className={styles.homeButton}
            onClick={() => navigate('/')}
          >
            Voltar para Home
          </button>
        </div>
        <div className={styles.illustration}>
          <div className={styles.icon}>🔍</div>
        </div>
      </div>
    </MainLayout>
  )
}

export default NotFound
