import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

vi.mock('@/api/client', () => ({
  apiClient: {
    synthesize: vi.fn(),
    healthCheck: vi.fn().mockResolvedValue({
      status: 'healthy',
      version: '0.1.0',
      tts_model_loaded: true,
      device: 'cpu',
    }),
  },
}))

describe('App', () => {
  it('renders header with title', () => {
    render(<App />)
    expect(screen.getByText('VoiceStudio')).toBeInTheDocument()
    expect(screen.getByText(/Open-source, fully-local ElevenLabs alternative/)).toBeInTheDocument()
  })

  it('renders health status', () => {
    render(<App />)
    expect(screen.getByText('Checking TTS service...')).toBeInTheDocument()
  })

  it('renders TTS form', () => {
    render(<App />)
    expect(screen.getByLabelText('Text to Synthesize')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Generate Speech' })).toBeInTheDocument()
  })

  it('renders footer with links', () => {
    render(<App />)
    expect(screen.getByText('VoiceStudio v0.1.0 — Alan Vo | AI & Machine Learning')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'GitHub' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'API Docs' })).toBeInTheDocument()
  })
})