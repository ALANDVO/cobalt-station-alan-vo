# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

skeleton-tts

## Roadmap

### skeleton-tts — FastAPI/React skeleton with basic TTS synthesis workflow

Status: in_progress

Acceptance:
- FastAPI backend runs with /health and /api/v1/tts/synthesize endpoints
- React frontend builds and serves UI with text input and audio playback
- Local TTS engine (Coqui TTS) synthesizes speech from text
- Docker compose runs backend, frontend, and Keycloak
- Backend and frontend tests pass
- README has install/run/test steps

### voice-cloning — Voice cloning with reference audio

Status: planned

Acceptance:
- Upload reference audio and clone voice
- Synthesize speech with cloned voice
- Manage voice profiles

### transcription — Speech-to-text transcription workflow

Status: planned

Acceptance:
- Upload audio/video and transcribe
- Support multiple languages
- Export transcripts as SRT/VTT/TXT

### video-dubbing — Video dubbing pipeline

Status: planned

Acceptance:
- Extract audio from video
- Transcribe, translate, synthesize dubbed audio
- Merge dubbed audio back to video

### audiobook-creation — Audiobook creation from text documents

Status: planned

Acceptance:
- Import EPUB/PDF/TXT documents
- Split into chapters
- Synthesize each chapter with voice selection
- Export as M4B/MP3 chapters

### auth-oidc — OIDC authentication with Keycloak

Status: planned

Acceptance:
- Keycloak realm configured
- Backend validates JWT tokens
- Frontend PKCE login flow
- Role-based access (viewer/operator/admin)

