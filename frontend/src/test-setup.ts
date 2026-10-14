import '@testing-library/jest-dom'
import { vi } from 'vitest'

vi.mock('@/api/client', () => ({
  apiClient: {
    synthesize: vi.fn(),
    healthCheck: vi.fn(),
  },
}))