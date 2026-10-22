declare global {
  interface ImportMetaEnv {
    readonly VITE_API_URL: string
  }
  interface ImportMeta {
    readonly env: ImportMetaEnv
  }
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export interface TTSRequest {
  text: string
  language: string
  speaker_wav?: string
  speed: number
}

export interface TTSResponse {
  audio_base64: string
  duration_seconds: number
  sample_rate: number
  language: string
  text_length: number
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  version: string
  tts_model_loaded: boolean
  device: string
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  async synthesize(request: TTSRequest): Promise<TTSResponse> {
    return this.request<TTSResponse>('/api/v1/tts/synthesize', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async healthCheck(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/api/v1/tts/health')
  }

  async generalHealth(): Promise<{ status: string; version: string }> {
    return this.request('/health')
  }
}

export const apiClient = new ApiClient()