import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { HealthStatus } from './HealthStatus'
import { apiClient } from '@/api/client'

vi.mock('@/api/client', () => ({
  apiClient: {
    synthesize: vi.fn(),
    healthCheck: vi.fn(),
  },
}))

const mockHealthCheck = vi.mocked(apiClient.healthCheck)

describe('HealthStatus', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading state initially', () => {
    render(<HealthStatus />)

    expect(screen.getByText('Checking TTS service...')).toBeInTheDocument()
  })

  it('shows healthy status when API returns healthy', async () => {
    mockHealthCheck.mockResolvedValue({
      status: 'healthy',
      version: '0.1.0',
      tts_model_loaded: true,
      device: 'cpu',
    })

    render(<HealthStatus />)

    await waitFor(() => {
      expect(screen.getByText('healthy')).toBeInTheDocument()
      expect(screen.getByText('Model: Loaded')).toBeInTheDocument()
      expect(screen.getByText('Device: cpu')).toBeInTheDocument()
    })
  })

  it('shows degraded status when model not loaded', async () => {
    mockHealthCheck.mockResolvedValue({
      status: 'degraded',
      version: '0.1.0',
      tts_model_loaded: false,
      device: 'cpu',
    })

    render(<HealthStatus />)

    await waitFor(() => {
      expect(screen.getByText('degraded')).toBeInTheDocument()
      expect(screen.getByText('Model: Not Loaded')).toBeInTheDocument()
    })
  })

  it('shows error when API fails', async () => {
    mockHealthCheck.mockRejectedValue(new Error('Connection refused'))

    render(<HealthStatus />)

    await waitFor(() => {
      expect(screen.getByText('Unavailable')).toBeInTheDocument()
      expect(screen.getByText('Connection refused')).toBeInTheDocument()
    })
  })
})