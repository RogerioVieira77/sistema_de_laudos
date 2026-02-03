import { useState } from 'react'
import { ChevronDown, ChevronUp, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import styles from './ResultCard.module.css'

function ResultCard({
  id = 'sample-001',
  fileName = 'contrato_exemplo.pdf',
  status = 'concluído',
  verdict = 'aprovado',
  confidence = 98.5,
  summary = 'Contrato válido e dentro dos padrões legais',
  findings = [
    { type: 'ok', title: 'Assinatura Digital', description: 'Assinatura válida e verificada' },
    { type: 'ok', title: 'Datas Consistentes', description: 'Datas de início e fim estão em ordem' },
    { type: 'warning', title: 'Cláusula Modificada', description: 'Cláusula 3.2 foi alterada manualmente' },
    { type: 'ok', title: 'Identificação', description: 'Partes identificadas corretamente' },
  ],
  processedAt = '2024-02-03T14:30:00Z',
  processingTime = '2m 34s'
}) {
  const [expanded, setExpanded] = useState({
    findings: false,
    details: false,
  })

  const getVerdictIcon = () => {
    switch (verdict?.toLowerCase()) {
      case 'aprovado':
        return <CheckCircle size={24} className={styles.iconSuccess} />
      case 'com_ressalvas':
        return <AlertCircle size={24} className={styles.iconWarning} />
      case 'reprovado':
        return <AlertCircle size={24} className={styles.iconError} />
      default:
        return <Clock size={24} className={styles.iconInfo} />
    }
  }

  const getVerdictLabel = () => {
    const labels = {
      'aprovado': { text: '✅ Aprovado', class: styles.approved },
      'com_ressalvas': { text: '⚠️ Com Ressalvas', class: styles.warning },
      'reprovado': { text: '❌ Reprovado', class: styles.rejected },
      'processando': { text: '⏳ Processando', class: styles.processing },
    }
    return labels[verdict?.toLowerCase()] || labels.processando
  }

  const toggleSection = (section) => {
    setExpanded(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const verdictInfo = getVerdictLabel()
  const okCount = findings.filter(f => f.type === 'ok').length
  const warningCount = findings.filter(f => f.type === 'warning').length
  const errorCount = findings.filter(f => f.type === 'error').length

  return (
    <div className={styles.card}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.verdictIcon}>
            {getVerdictIcon()}
          </div>
          <div className={styles.headerInfo}>
            <div className={styles.fileName}>{fileName}</div>
            <div className={styles.fileId}>ID: {id}</div>
          </div>
        </div>
        <div className={`${styles.verdict} ${verdictInfo.class}`}>
          {verdictInfo.text}
        </div>
      </div>

      {/* Confidence Bar */}
      <div className={styles.confidenceSection}>
        <div className={styles.confidenceLabel}>
          <span>Confiança da Análise</span>
          <span className={styles.confidenceValue}>{confidence}%</span>
        </div>
        <div className={styles.confidenceBar}>
          <div 
            className={styles.confidenceFill}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Summary */}
      <div className={styles.summary}>
        <p>{summary}</p>
      </div>

      {/* Stats Row */}
      <div className={styles.statsRow}>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>✅</span>
          <div>
            <div className={styles.statValue}>{okCount}</div>
            <div className={styles.statLabel}>Conformidades</div>
          </div>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>⚠️</span>
          <div>
            <div className={styles.statValue}>{warningCount}</div>
            <div className={styles.statLabel}>Avisos</div>
          </div>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>❌</span>
          <div>
            <div className={styles.statValue}>{errorCount}</div>
            <div className={styles.statLabel}>Problemas</div>
          </div>
        </div>
        <div className={styles.statItem}>
          <span className={styles.statIcon}>⏱️</span>
          <div>
            <div className={styles.statValue}>{processingTime}</div>
            <div className={styles.statLabel}>Tempo Proc.</div>
          </div>
        </div>
      </div>

      {/* Findings Section */}
      <div className={styles.section}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('findings')}
        >
          <span className={styles.sectionTitle}>📋 Detalhes da Análise</span>
          {expanded.findings ? (
            <ChevronUp size={20} />
          ) : (
            <ChevronDown size={20} />
          )}
        </button>

        {expanded.findings && (
          <div className={styles.sectionContent}>
            {findings.map((finding, idx) => (
              <div 
                key={idx}
                className={`${styles.finding} ${styles[`finding${finding.type}`]}`}
              >
                <div className={styles.findingIcon}>
                  {finding.type === 'ok' && '✅'}
                  {finding.type === 'warning' && '⚠️'}
                  {finding.type === 'error' && '❌'}
                </div>
                <div className={styles.findingContent}>
                  <div className={styles.findingTitle}>{finding.title}</div>
                  <div className={styles.findingDescription}>
                    {finding.description}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Details Section */}
      <div className={styles.section}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('details')}
        >
          <span className={styles.sectionTitle}>📊 Informações Técnicas</span>
          {expanded.details ? (
            <ChevronUp size={20} />
          ) : (
            <ChevronDown size={20} />
          )}
        </button>

        {expanded.details && (
          <div className={styles.sectionContent}>
            <div className={styles.detailsGrid}>
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>Data Processamento</span>
                <span className={styles.detailValue}>
                  {new Date(processedAt).toLocaleDateString('pt-BR')}
                </span>
              </div>
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>Hora Processamento</span>
                <span className={styles.detailValue}>
                  {new Date(processedAt).toLocaleTimeString('pt-BR')}
                </span>
              </div>
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>Status</span>
                <span className={styles.detailValue}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </span>
              </div>
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>Tempo Total</span>
                <span className={styles.detailValue}>{processingTime}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ResultCard
