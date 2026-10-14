import { TTSForm } from '@/components/TTSForm'
import { HealthStatus } from '@/components/HealthStatus'

export default function App() {
  return (
    <div className="container">
      <header className="header">
        <h1>VoiceStudio</h1>
        <p>Open-source, fully-local ElevenLabs alternative — voice cloning, TTS, transcription & audiobook creation</p>
      </header>

      <main>
        <HealthStatus />
        <TTSForm />
      </main>

      <footer style={{ textAlign: 'center', marginTop: '3rem', paddingTop: '1.5rem', borderTop: '1px solid var(--color-border)', color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
        <p>VoiceStudio v0.1.0 — Alan Vo | AI & Machine Learning</p>
        <p style={{ marginTop: '0.25rem' }}>
          <a href="https://github.com/ALANDVO/cobalt-station-alan-vo" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-primary)' }}>
            GitHub
          </a>
          {' | '}
          <a href="/docs" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--color-primary)' }}>
            API Docs
          </a>
        </p>
      </footer>
    </div>
  )
}