import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { ArrowLeft, Share2, Trash2 } from 'lucide-react'
import MainLayout from '../components/layouts/MainLayout'
import ResultCard from '../components/resultado/ResultCard'
import Statistics from '../components/resultado/Statistics'
import Timeline from '../components/resultado/Timeline'
import DownloadButton from '../components/resultado/DownloadButton'
import styles from './Resultado.module.css'

function Resultado() {
  const { id } = useParams()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Mock data - em produção, buscar da API
  useEffect(() => {
    const mockResult = {
      id: id || 'RESULTADO_20240115_001',
      fileName: 'Contrato_Aluguel_2024.pdf',
      fileSize: '2.5 MB',
      status: 'concluído',
      verdict: 'aprovado', // aprovado, com_ressalvas, reprovado, processando
      confidence: 96,
      summary:
        'Contrato de aluguel analisado com sucesso. Documento possui todas as cláusulas legais obrigatórias e está em conformidade com a legislação vigente. Não foram detectadas inconsistências críticas.',
      findings: [
        {
          type: 'ok',
          title: 'Cláusulas Legais Obrigatórias',
          description:
            'Todas as cláusulas legais obrigatórias estão presentes e corretamente redigidas.',
        },
        {
          type: 'ok',
          title: 'Identificação das Partes',
          description:
            'Identificação clara e completa de todas as partes envolvidas no contrato.',
        },
        {
          type: 'ok',
          title: 'Validade de Assinatura',
          description:
            'Assinaturas digitais verificadas e validadas conforme padrão.',
        },
        {
          type: 'warning',
          title: 'Data de Expiração',
          description:
            'Contrato expirará em 12 meses. Recomenda-se análise para renovação.',
        },
        {
          type: 'ok',
          title: 'Dados Financeiros',
          description:
            'Valores de aluguel e depósitos caução estão claramente especificados.',
        },
      ],
      processedAt: new Date().toISOString(),
      processingTime: '6,5 segundos',
      pagesAnalyzed: 8,
      dataExtracted: 34,
      entitiesFound: 12,
      accuracy: 96.8,
      timestamps: {
        started: new Date(Date.now() - 10000).toLocaleString('pt-BR'),
        completed: new Date().toLocaleString('pt-BR'),
        duration: '6.5s',
      },
      steps: [
        {
          id: 1,
          label: 'Enviado',
          status: 'completed',
          time: new Date(Date.now() - 10000).toLocaleTimeString('pt-BR'),
        },
        {
          id: 2,
          label: 'Validação',
          status: 'completed',
          time: new Date(Date.now() - 8500).toLocaleTimeString('pt-BR'),
        },
        {
          id: 3,
          label: 'Análise',
          status: 'completed',
          time: new Date(Date.now() - 5000).toLocaleTimeString('pt-BR'),
        },
        {
          id: 4,
          label: 'Geolocalização',
          status: 'completed',
          time: new Date(Date.now() - 2000).toLocaleTimeString('pt-BR'),
        },
        {
          id: 5,
          label: 'Parecer',
          status: 'completed',
          time: new Date(Date.now() - 500).toLocaleTimeString('pt-BR'),
        },
        {
          id: 6,
          label: 'Finalizado',
          status: 'completed',
          time: new Date().toLocaleTimeString('pt-BR'),
        },
      ],
    }

    // Simular delay de carregamento
    setTimeout(() => {
      setResult(mockResult)
      setLoading(false)
    }, 500)
  }, [id])

  const handleDownload = async () => {
    // Em produção, fazer download real da API
    console.log('Downloading result:', id)
    // await api.downloadResult(id)
  }

  const handleDelete = async () => {
    if (
      window.confirm(
        'Tem certeza que deseja excluir este resultado? Esta ação não pode ser desfeita.'
      )
    ) {
      // Em produção, deletar via API
      console.log('Deleting result:', id)
      // await api.deleteResult(id)
      // navigate('/contratos')
    }
  }

  const handleShare = async () => {
    // Em produção, compartilhar resultado
    console.log('Sharing result:', id)
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Resultado - ${result?.fileName}`,
          text: `Parecer jurídico para ${result?.fileName}`,
          url: window.location.href,
        })
      } catch (err) {
        console.log('Share cancelled or failed:', err)
      }
    }
  }

  if (loading) {
    return (
      <MainLayout activeItem="resultados">
        <div className={styles.loadingContainer}>
          <div className={styles.spinner} />
          <p>Carregando resultado...</p>
        </div>
      </MainLayout>
    )
  }

  if (error || !result) {
    return (
      <MainLayout activeItem="resultados">
        <div className={styles.errorContainer}>
          <h2>❌ Erro ao Carregar Resultado</h2>
          <p>{error || 'Resultado não encontrado.'}</p>
          <a href="/contratos" className={styles.backLink}>
            ← Voltar para Contratos
          </a>
        </div>
      </MainLayout>
    )
  }

  return (
    <MainLayout activeItem="resultados">
      <div className={styles.pageContainer}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerTop}>
            <a href="/contratos" className={styles.backButton}>
              <ArrowLeft size={20} />
              <span>Voltar</span>
            </a>
            <h1 className={styles.title}>Resultado da Análise</h1>
            <div className={styles.spacer} />
          </div>

          {/* Action Buttons */}
          <div className={styles.actionButtons}>
            <button
              className={styles.actionBtn}
              onClick={handleShare}
              title="Compartilhar resultado"
            >
              <Share2 size={18} />
              <span>Compartilhar</span>
            </button>
            <button
              className={`${styles.actionBtn} ${styles.deleteBtn}`}
              onClick={handleDelete}
              title="Excluir resultado"
            >
              <Trash2 size={18} />
              <span>Excluir</span>
            </button>
          </div>
        </div>

        {/* Subtitle */}
        <div className={styles.subtitle}>
          <span className={styles.resultId}>ID: {result.id}</span>
          <span className={styles.resultDate}>
            {new Date(result.processedAt).toLocaleDateString('pt-BR')}
          </span>
        </div>

        {/* Main Content Grid */}
        <div className={styles.contentGrid}>
          {/* Left Column - Results and Timeline */}
          <div className={styles.mainColumn}>
            {/* Result Card */}
            <ResultCard
              id={result.id}
              fileName={result.fileName}
              status={result.status}
              verdict={result.verdict}
              confidence={result.confidence}
              summary={result.summary}
              findings={result.findings}
              processedAt={result.processedAt}
              processingTime={result.processingTime}
            />

            {/* Timeline */}
            <Timeline steps={result.steps} />

            {/* Download Section */}
            <div className={styles.downloadSection}>
              <h3 className={styles.sectionTitle}>📥 Download do Parecer</h3>
              <DownloadButton
                fileName={result.fileName}
                fileSize={result.fileSize}
                onDownload={handleDownload}
              />
            </div>
          </div>

          {/* Right Column - Statistics */}
          <div className={styles.sideColumn}>
            <Statistics
              pagesAnalyzed={result.pagesAnalyzed}
              dataExtracted={result.dataExtracted}
              entitiesFound={result.entitiesFound}
              accuracy={result.accuracy}
              processingTime={result.processingTime}
              fileSize={result.fileSize}
              timestamps={result.timestamps}
            />
          </div>
        </div>
      </div>
    </MainLayout>
  )
}

export default Resultado
