import { useEffect, useState } from 'react'
import { apiClient, HealthResponse } from '@/api/client'

export function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await apiClient.healthCheck()
        setHealth(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Health check failed')
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span className="loading-spinner" style={{ width: '1.25rem', height: '1.25rem' }} />
          <span>Checking TTS service...</span>
        </div>
      </div>
    )
  }

  if (error || !health) {
    return (
      <div className="card">
        <div className="status-badge status-unhealthy">Unavailable</div>
        {error && <p style={{ marginTop: '0.5rem', color: 'var(--color-error)', fontSize: '0.875rem' }}>{error}</p>}
      </div>
    )
  }

  const statusClass = `status-${health.status}`

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
        <span className={`status-badge ${statusClass}`}>{health.status}</span>
        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
          <span>Model: {health.tts_model_loaded ? 'Loaded' : 'Not Loaded'}</span>
          <span style={{ marginLeft: '1rem' }}>Device: {health.device}</span>
          <span style={{ marginLeft: '1rem' }}>Version: {health.version}</span>
        </div>
      </div>
    </div>
  )
}