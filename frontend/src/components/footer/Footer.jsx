import styles from './Footer.module.css'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.content}>
          <p className={styles.copyright}>
            © {currentYear} Sistema de Laudos. Todos os direitos reservados.
          </p>

          <div className={styles.links}>
            <a href="/docs" target="_blank" rel="noopener noreferrer">
              Documentação
            </a>
            <a href="/github" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
            <a href="/contato">
              Contato
            </a>
          </div>

          <div className={styles.status}>
            <span className={styles.statusBadge}>
              <span className={styles.statusDot}></span>
              API Online
            </span>
          </div>
        </div>

        <div className={styles.bottom}>
          <span className={styles.version}>v1.0.0</span>
          <span className={styles.divider}>•</span>
          <span className={styles.timestamp}>
            {new Date().toLocaleDateString('pt-BR')}
          </span>
        </div>
      </div>
    </footer>
  )
}
