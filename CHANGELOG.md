# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — 2026-10-22

### Added
- FastAPI backend with /health and /api/v1/tts/synthesize endpoints
- React + TypeScript + Vite frontend with text-to-speech UI
- Coqui XTTS v2 integration for multilingual speech synthesis (646+ languages)
- Voice cloning support via reference audio upload (base64-encoded WAV)
- Docker Compose with backend, frontend, and Keycloak services
- Backend tests (17 passing): health checks, OpenAPI schema, TTS models, service, API, and integration
- Frontend tests (18 passing): TTSForm, HealthStatus, and App components
- CI/CD workflow (.github/workflows/ci.yml) with backend tests, frontend build/test, and Docker builds
- Health check endpoints with model load status
- Input validation for TTS requests (text, language, speed, speaker_wav)

### Fixed
- TTS model loading with non-interactive CPML license acceptance
- Lazy TTS service initialization to avoid model load during tests
- Frontend test mocks and timer handling for HealthStatus component
- TypeScript configuration for Vite path aliases and ImportMeta types

## [Unreleased]

### Added
- Initial project skeleton with FastAPI backend and React frontend
- Text-to-speech synthesis using Coqui XTTS v2
- Docker Compose setup with backend, frontend, and Keycloak
- Basic test infrastructure

## [0.1.0] - 2026-10-14

### Added
- Project initialization
- Feature plan and roadmap (PLAN.md)
- Core configuration files