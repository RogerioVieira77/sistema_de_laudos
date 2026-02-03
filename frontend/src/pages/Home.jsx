import MainLayout from '../components/layouts/MainLayout'

export default function Home() {
  return (
    <MainLayout activeItem="home">
      <div className="home-page">
        <div style={{ textAlign: 'center', paddingTop: '2rem' }}>
          <h1 style={{ 
            fontSize: '2.5rem',
            marginBottom: '1rem',
            color: '#2c3e50'
          }}>
            Bem-vindo ao Sistema de Laudos
          </h1>
          
          <p style={{
            fontSize: '1.2rem',
            color: '#7f8c8d',
            marginBottom: '3rem'
          }}>
            Ferramenta inteligente para análise de documentos e geolocalização
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '2rem',
            marginTop: '2rem'
          }}>
            {/* Card 1 */}
            <div style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📤</div>
              <h3>Upload Documentos</h3>
              <p>Faça upload de PDFs para análise automática</p>
              <a href="/upload" style={{
                display: 'inline-block',
                marginTop: '1rem',
                padding: '0.75rem 1.5rem',
                backgroundColor: '#667eea',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '4px',
                transition: 'background-color 0.2s'
              }}>
                Começar →
              </a>
            </div>

            {/* Card 2 */}
            <div style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📋</div>
              <h3>Ver Contratos</h3>
              <p>Visualize todos os contratos analisados</p>
              <a href="/contratos" style={{
                display: 'inline-block',
                marginTop: '1rem',
                padding: '0.75rem 1.5rem',
                backgroundColor: '#667eea',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '4px',
                transition: 'background-color 0.2s'
              }}>
                Ver Lista →
              </a>
            </div>

            {/* Card 3 */}
            <div style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🗺️</div>
              <h3>Geolocalização</h3>
              <p>Análise de localização e distâncias</p>
              <a href="/geolocation" style={{
                display: 'inline-block',
                marginTop: '1rem',
                padding: '0.75rem 1.5rem',
                backgroundColor: '#667eea',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '4px',
                transition: 'background-color 0.2s'
              }}>
                Explorar →
              </a>
            </div>
          </div>

          <div style={{
            marginTop: '4rem',
            padding: '2rem',
            background: 'white',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <h2>Status do Sistema</h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
              marginTop: '1rem'
            }}>
              <div>
                <span style={{ fontSize: '0.9rem', color: '#7f8c8d' }}>API Backend</span>
                <p style={{ margin: '0.5rem 0 0 0', color: '#27ae60', fontWeight: 'bold' }}>✓ Online</p>
              </div>
              <div>
                <span style={{ fontSize: '0.9rem', color: '#7f8c8d' }}>Base de Dados</span>
                <p style={{ margin: '0.5rem 0 0 0', color: '#27ae60', fontWeight: 'bold' }}>✓ Conectado</p>
              </div>
              <div>
                <span style={{ fontSize: '0.9rem', color: '#7f8c8d' }}>Cache</span>
                <p style={{ margin: '0.5rem 0 0 0', color: '#27ae60', fontWeight: 'bold' }}>✓ Ativo</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
