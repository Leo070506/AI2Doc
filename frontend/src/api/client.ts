import { ApiError, isErrorPayload, type ConvertResult, type TemplateName } from './types'

async function parseResponse(response: Response): Promise<ConvertResult> {
  let body: unknown
  try {
    body = await response.json()
  } catch {
    throw new ApiError('The server returned an unreadable response.')
  }

  if (!response.ok) {
    if (isErrorPayload(body)) throw new ApiError(body.error.message, body.error.code)
    throw new ApiError('Document generation failed. Please try again.')
  }
  return body as ConvertResult
}

export async function convertText(content: string, template: TemplateName): Promise<ConvertResult> {
  const response = await fetch('/api/convert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, template }),
  })
  return parseResponse(response)
}

export async function convertFile(file: File, template: TemplateName): Promise<ConvertResult> {
  const form = new FormData()
  form.append('file', file)
  form.append('template', template)
  const response = await fetch('/api/convert', { method: 'POST', body: form })
  return parseResponse(response)
}
