import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { TTSForm } from './TTSForm'
import { apiClient } from '@/api/client'

vi.mock('@/api/client', () => ({
  apiClient: {
    synthesize: vi.fn(),
    healthCheck: vi.fn(),
  },
}))

const mockSynthesize = vi.mocked(apiClient.synthesize)

describe('TTSForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders form with all fields', () => {
    render(<TTSForm />)

    expect(screen.getByLabelText('Text to Synthesize')).toBeInTheDocument()
    expect(screen.getByLabelText('Language')).toBeInTheDocument()
    expect(screen.getByLabelText(/Speed:/)).toBeInTheDocument()
    expect(screen.getByLabelText('Reference Audio (Optional - Voice Cloning)')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Generate Speech' })).toBeInTheDocument()
  })

  it('shows character count', () => {
    render(<TTSForm />)

    const textarea = screen.getByLabelText('Text to Synthesize')
    fireEvent.change(textarea, { target: { value: 'Hello world' } })

    expect(screen.getByText('11/5000 characters')).toBeInTheDocument()
  })

  it('disables generate button when text is empty', () => {
    render(<TTSForm />)

    const button = screen.getByRole('button', { name: 'Generate Speech' })
    expect(button).toBeDisabled()
  })

  it('enables generate button when text is entered', () => {
    render(<TTSForm />)

    const textarea = screen.getByLabelText('Text to Synthesize')
    fireEvent.change(textarea, { target: { value: 'Hello' } })

    const button = screen.getByRole('button', { name: 'Generate Speech' })
    expect(button).not.toBeDisabled()
  })

  it('calls synthesize API on submit', async () => {
    mockSynthesize.mockResolvedValue({
      audio_base64: 'dGVzdA==',
      duration_seconds: 1.5,
      sample_rate: 24000,
      language: 'en',
      text_length: 5,
    })

    render(<TTSForm />)

    const textarea = screen.getByLabelText('Text to Synthesize')
    fireEvent.change(textarea, { target: { value: 'Hello' } })

    const button = screen.getByRole('button', { name: 'Generate Speech' })
    fireEvent.click(button)

    await waitFor(() => {
      expect(mockSynthesize).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'Hello',
          language: 'en',
          speed: 1.0,
        })
      )
    })
  })

  it('shows audio player after successful synthesis', async () => {
    mockSynthesize.mockResolvedValue({
      audio_base64: 'dGVzdA==',
      duration_seconds: 1.5,
      sample_rate: 24000,
      language: 'en',
      text_length: 5,
    })

    render(<TTSForm />)

    const textarea = screen.getByLabelText('Text to Synthesize')
    fireEvent.change(textarea, { target: { value: 'Hello' } })

    const button = screen.getByRole('button', { name: 'Generate Speech' })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Download WAV' })).toBeInTheDocument()
      expect(screen.getByText(/Duration: 1\.5s/)).toBeInTheDocument()
    })
  })

  it('shows error message on API failure', async () => {
    mockSynthesize.mockRejectedValue(new Error('Synthesis failed'))

    render(<TTSForm />)

    const textarea = screen.getByLabelText('Text to Synthesize')
    fireEvent.change(textarea, { target: { value: 'Hello' } })

    const button = screen.getByRole('button', { name: 'Generate Speech' })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Synthesis failed')).toBeInTheDocument()
    })
  })

  it('handles language selection', () => {
    render(<TTSForm />)

    const select = screen.getByLabelText('Language')
    fireEvent.change(select, { target: { value: 'es' } })

    expect(select).toHaveValue('es')
  })

  it('handles speed slider', () => {
    render(<TTSForm />)

    const slider = screen.getByLabelText(/Speed:/)
    fireEvent.change(slider, { target: { value: '1.5' } })

    expect(screen.getByText('Speed: 1.5x')).toBeInTheDocument()
  })

  it('clears result when clear button clicked', async () => {
    mockSynthesize.mockResolvedValue({
      audio_base64: 'dGVzdA==',
      duration_seconds: 1.5,
      sample_rate: 24000,
      language: 'en',
      text_length: 5,
    })

    render(<TTSForm />)

    const textarea = screen.getByLabelText('Text to Synthesize')
    fireEvent.change(textarea, { target: { value: 'Hello' } })

    fireEvent.click(screen.getByRole('button', { name: 'Generate Speech' }))

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Download WAV' })).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: 'Clear Result' }))

    expect(screen.queryByRole('button', { name: 'Download WAV' })).not.toBeInTheDocument()
  })
})