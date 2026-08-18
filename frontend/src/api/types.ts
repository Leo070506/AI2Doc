export type TemplateName = 'academic' | 'report' | 'notes'

export interface ConvertResult {
  status: 'success'
  file: string
  filename: string
  expires_at: string
}

interface ErrorPayload {
  status: 'error'
  error: {
    code: string
    message: string
    request_id?: string
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code = 'request_failed',
  ) {
    super(message)
  }
}

export function isErrorPayload(value: unknown): value is ErrorPayload {
  if (!value || typeof value !== 'object') return false
  const error = (value as { error?: unknown }).error
  return Boolean(
    error &&
      typeof error === 'object' &&
      typeof (error as { message?: unknown }).message === 'string',
  )
}
