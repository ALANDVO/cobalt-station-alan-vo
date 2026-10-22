import { vi } from 'vitest'
import '@testing-library/jest-dom'

vi.mock('@/api/client', () => ({
  apiClient: {
    synthesize: vi.fn(),
    healthCheck: vi.fn(),
  },
}))