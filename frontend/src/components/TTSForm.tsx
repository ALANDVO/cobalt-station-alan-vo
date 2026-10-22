import { useState, useCallback } from 'react'
import { apiClient, TTSRequest, TTSResponse } from '@/api/client'

export function TTSForm() {
  const [text, setText] = useState('')
  const [language, setLanguage] = useState('en')
  const [speed, setSpeed] = useState(1.0)
  const [speakerWav, setSpeakerWav] = useState<string | null>(null)
  const [speakerWavName, setSpeakerWavName] = useState<string | null>(null)
  const [result, setResult] = useState<TTSResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'pl', name: 'Polish' },
    { code: 'tr', name: 'Turkish' },
    { code: 'ru', name: 'Russian' },
    { code: 'nl', name: 'Dutch' },
    { code: 'cs', name: 'Czech' },
    { code: 'ar', name: 'Arabic' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'hu', name: 'Hungarian' },
    { code: 'hi', name: 'Hindi' },
  ]

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.wav')) {
      setError('Reference audio must be a WAV file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Reference audio too large (max 10MB)')
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      const base64 = (reader.result as string).split(',')[1]
      setSpeakerWav(base64)
      setSpeakerWavName(file.name)
      setError(null)
    }
    reader.readAsDataURL(file)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const request: TTSRequest = {
        text: text.trim(),
        language,
        speed,
        speaker_wav: speakerWav || undefined,
      }

      const response = await apiClient.synthesize(request)
      setResult(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Synthesis failed')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setResult(null)
    setError(null)
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2 className="card-title">Text-to-Speech Synthesis</h2>

      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label htmlFor="text" className="form-label">Text to Synthesize</label>
        <textarea
          id="text"
          className="form-textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text to convert to speech (max 5000 characters)..."
          maxLength={5000}
          required
        />
        <p className="form-help">{text.length}/5000 characters</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div className="form-group">
          <label htmlFor="language" className="form-label">Language</label>
          <select
            id="language"
            className="form-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.name} ({lang.code})
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="speed" className="form-label">Speed: {speed.toFixed(1)}x</label>
          <input
            id="speed"
            type="range"
            className="form-input"
            min="0.5"
            max="2.0"
            step="0.1"
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="speaker-wav" className="form-label">Reference Audio (Optional - Voice Cloning)</label>
        <input
          id="speaker-wav"
          type="file"
          accept=".wav"
          onChange={handleFileChange}
          className="form-input"
        />
        {speakerWavName && (
          <p className="form-help">
            Using: {speakerWavName}
            <button
              type="button"
              onClick={() => {
                setSpeakerWav(null)
                setSpeakerWavName(null)
              }}
              style={{ marginLeft: '0.5rem', padding: '0.125rem 0.5rem', fontSize: '0.75rem' }}
            >
              Remove
            </button>
          </p>
        )}
        <p className="form-help">Upload a WAV file (6+ seconds recommended) to clone a voice</p>
      </div>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !text.trim()}
        >
          {loading && <span className="loading-spinner" />}
          {loading ? 'Synthesizing...' : 'Generate Speech'}
        </button>
        {result && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleClear}
          >
            Clear Result
          </button>
        )}
      </div>

      {result && (
        <AudioPlayer
          audioBase64={result.audio_base64}
          duration={result.duration_seconds}
          sampleRate={result.sample_rate}
        />
      )}
    </form>
  )
}

function AudioPlayer({ audioBase64, duration, sampleRate }: { audioBase64: string; duration: number; sampleRate: number }) {
  const audioSrc = `data:audio/wav;base64,${audioBase64}`

  return (
    <div className="card" style={{ marginTop: '1rem' }}>
      <h3 className="card-title">Generated Audio</h3>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <span className="status-badge status-healthy">Ready</span>
        <span style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
          Duration: {duration.toFixed(1)}s | Sample Rate: {sampleRate}Hz
        </span>
        <a
          href={audioSrc}
          download={`voicestudio-${Date.now()}.wav`}
          className="btn btn-secondary"
          style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
          role="button"
        >
          Download WAV
        </a>
      </div>
      <audio controls className="audio-player" src={audioSrc} />
    </div>
  )
}