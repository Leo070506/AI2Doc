import { mkdir, readFile, writeFile } from 'node:fs/promises'

const baseUrl = (process.env.AI2DOC_E2E_BASE_URL ?? 'http://localhost:8080').replace(/\/$/, '')
const debugUrl = (process.env.CHROME_DEBUG_URL ?? 'http://127.0.0.1:9222').replace(/\/$/, '')
const inputPath = process.env.AI2DOC_E2E_INPUT ?? 'examples/docker-release-example.md'
const artifactDir = process.env.AI2DOC_E2E_ARTIFACT_DIR ?? 'validation-artifacts'

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds))

class CdpClient {
  constructor(socket) {
    this.socket = socket
    this.nextId = 1
    this.pending = new Map()

    socket.addEventListener('message', (event) => {
      const message = JSON.parse(String(event.data))
      if (!message.id || !this.pending.has(message.id)) return
      const { resolve, reject, timer } = this.pending.get(message.id)
      clearTimeout(timer)
      this.pending.delete(message.id)
      if (message.error) reject(new Error(`${message.error.code}: ${message.error.message}`))
      else resolve(message.result)
    })
  }

  static async connect(webSocketUrl) {
    const socket = new WebSocket(webSocketUrl)
    await new Promise((resolve, reject) => {
      socket.addEventListener('open', resolve, { once: true })
      socket.addEventListener('error', reject, { once: true })
    })
    return new CdpClient(socket)
  }

  send(method, params = {}) {
    const id = this.nextId++
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id)
        reject(new Error(`CDP command timed out: ${method}`))
      }, 15_000)
      this.pending.set(id, { resolve, reject, timer })
      this.socket.send(JSON.stringify({ id, method, params }))
    })
  }

  async evaluate(expression) {
    const result = await this.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true,
    })
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text)
    return result.result.value
  }

  close() {
    this.socket.close()
  }
}

async function waitFor(client, expression, message, timeout = 20_000) {
  const deadline = Date.now() + timeout
  while (Date.now() < deadline) {
    if (await client.evaluate(`Boolean(${expression})`)) return
    await delay(250)
  }
  throw new Error(message)
}

async function main() {
  await mkdir(artifactDir, { recursive: true })
  const markdown = await readFile(inputPath, 'utf8')
  const targetResponse = await fetch(`${debugUrl}/json/new?${encodeURIComponent(baseUrl)}`, {
    method: 'PUT',
  })
  if (!targetResponse.ok) throw new Error(`Chrome target creation failed: ${targetResponse.status}`)
  const target = await targetResponse.json()
  const client = await CdpClient.connect(target.webSocketDebuggerUrl)

  try {
    await client.send('Page.enable')
    await client.send('Runtime.enable')
    await client.send('Page.navigate', { url: baseUrl })
    await waitFor(
      client,
      `document.readyState === 'complete' && document.querySelector('#markdown-content')`,
      'Vue converter did not render',
    )

    const markdownLiteral = JSON.stringify(markdown)
    const inputResult = await client.evaluate(`(() => {
      const textarea = document.querySelector('#markdown-content')
      const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set
      setter.call(textarea, ${markdownLiteral})
      textarea.dispatchEvent(new Event('input', { bubbles: true }))
      const academic = document.querySelector('input[name="template"][value="academic"]')
      academic.click()
      academic.dispatchEvent(new Event('change', { bubbles: true }))
      return { contentLength: textarea.value.length, academic: academic.checked }
    })()`)
    if (!inputResult.academic || inputResult.contentLength !== markdown.length) {
      throw new Error('Browser input or Academic template selection failed')
    }

    await waitFor(
      client,
      `!document.querySelector('button.generate-button').disabled`,
      'Generate button did not become enabled',
    )
    await client.evaluate(`document.querySelector('button.generate-button').click()`)
    await waitFor(
      client,
      `document.querySelector('.success-message a[download]') || document.querySelector('.error-message')`,
      'Browser conversion did not finish',
      60_000,
    )

    const result = await client.evaluate(`(() => {
      const error = document.querySelector('.error-message')?.textContent?.trim() ?? ''
      const link = document.querySelector('.success-message a[download]')
      return {
        error,
        ready: document.querySelector('.success-message strong')?.textContent?.trim() ?? '',
        href: link?.href ?? '',
        filename: link?.getAttribute('download') ?? '',
        academic: document.querySelector('input[value="academic"]')?.checked ?? false,
      }
    })()`)
    if (result.error) throw new Error(`Browser conversion failed: ${result.error}`)
    if (!result.href.includes('/api/files/') || result.ready !== 'Your document is ready.') {
      throw new Error('Browser did not expose a valid one-time DOCX link')
    }
    if (!result.academic) throw new Error('Academic template was not retained')

    const screenshot = await client.send('Page.captureScreenshot', {
      format: 'png',
      captureBeyondViewport: true,
    })
    await writeFile(`${artifactDir}/browser-e2e.png`, Buffer.from(screenshot.data, 'base64'))
    await writeFile(
      `${artifactDir}/browser-e2e.json`,
      `${JSON.stringify({ ...result, contentLength: inputResult.contentLength }, null, 2)}\n`,
      'utf8',
    )
    console.log(JSON.stringify(result, null, 2))
  } finally {
    client.close()
  }
}

await main()
