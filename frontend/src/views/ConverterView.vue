<script setup lang="ts">
import { computed, ref } from 'vue'

import { convertFile, convertText } from '../api/client'
import { ApiError, type ConvertResult, type TemplateName } from '../api/types'
import ContentInput from '../components/ContentInput.vue'
import TemplateSelector from '../components/TemplateSelector.vue'
import { isMarkdownFile, MAX_FILE_BYTES } from '../utils/files'

const mode = ref<'text' | 'file'>('text')
const content = ref('')
const file = ref<File | null>(null)
const template = ref<TemplateName>('report')
const isGenerating = ref(false)
const error = ref('')
const result = ref<ConvertResult | null>(null)

const canGenerate = computed(() => {
  if (isGenerating.value) return false
  return mode.value === 'text' ? Boolean(content.value.trim()) : file.value !== null
})

function validate(): string | null {
  if (mode.value === 'text' && !content.value.trim()) return 'Paste an AI response to continue.'
  if (mode.value === 'file') {
    if (!file.value) return 'Choose a Markdown file to continue.'
    if (!isMarkdownFile(file.value)) return 'Choose a .md or .markdown file.'
    if (file.value.size > MAX_FILE_BYTES) return 'File too large. The maximum size is 1 MB.'
  }
  return null
}

async function generate() {
  error.value = validate() ?? ''
  result.value = null
  if (error.value) return

  isGenerating.value = true
  try {
    result.value =
      mode.value === 'text'
        ? await convertText(content.value, template.value)
        : await convertFile(file.value as File, template.value)
  } catch (caught) {
    error.value = caught instanceof ApiError ? caught.message : 'Document generation failed. Please try again.'
  } finally {
    isGenerating.value = false
  }
}
</script>

<template>
  <div class="app-shell">
    <header class="site-header">
      <a class="brand" href="/" aria-label="AI2Doc home">
        <span class="brand-mark" aria-hidden="true">A2</span>
        <span>AI2Doc</span>
      </a>
      <span class="status-pill"><span></span> Web MVP</span>
    </header>

    <main>
      <section class="hero">
        <p class="eyebrow">AI TO PROFESSIONAL DOCUMENT</p>
        <h1>From thoughtful answer<br />to polished document.</h1>
        <p class="hero-copy">
          Turn Markdown from any AI assistant into a clean, template-based Word document—without
          installing anything.
        </p>
      </section>

      <form class="converter-card" @submit.prevent="generate">
        <ContentInput
          v-model:mode="mode"
          v-model:content="content"
          v-model:file="file"
        />
        <div class="rule"></div>
        <TemplateSelector v-model="template" />
        <div class="action-area">
          <div class="privacy-note">
            <span class="privacy-dot" aria-hidden="true"></span>
            Files are temporary and deleted after download.
          </div>
          <button class="generate-button" type="submit" :disabled="!canGenerate">
            <span v-if="isGenerating" class="spinner" aria-hidden="true"></span>
            {{ isGenerating ? 'Generating…' : 'Generate DOCX' }}
            <span v-if="!isGenerating" aria-hidden="true">→</span>
          </button>
        </div>

        <p v-if="error" class="message error-message" role="alert">{{ error }}</p>
        <div v-if="result" class="message success-message" role="status">
          <div>
            <strong>Your document is ready.</strong>
            <span>The link works once and expires automatically.</span>
          </div>
          <a :href="result.file" :download="result.filename">Download DOCX</a>
        </div>
      </form>
    </main>

    <footer>
      <span>AI2Doc · Open source document generation</span>
      <span>Markdown + Pandoc + DOCX templates</span>
    </footer>
  </div>
</template>
