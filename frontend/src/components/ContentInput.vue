<script setup lang="ts">
import { ref } from 'vue'

import { formatBytes } from '../utils/files'

defineProps<{
  mode: 'text' | 'file'
  content: string
  file: File | null
}>()

const emit = defineEmits<{
  'update:mode': [value: 'text' | 'file']
  'update:content': [value: string]
  'update:file': [value: File | null]
}>()

const fileInput = ref<HTMLInputElement | null>(null)

function selectFile(event: Event) {
  const input = event.target as HTMLInputElement
  emit('update:file', input.files?.[0] ?? null)
}

function clearFile() {
  emit('update:file', null)
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<template>
  <section aria-labelledby="content-heading">
    <div class="section-heading">
      <div>
        <p class="step-label">Step 01</p>
        <h2 id="content-heading">Add your AI response</h2>
      </div>
      <div class="mode-switch" aria-label="Input method">
        <button
          type="button"
          :class="{ active: mode === 'text' }"
          :aria-pressed="mode === 'text'"
          @click="emit('update:mode', 'text')"
        >
          Paste text
        </button>
        <button
          type="button"
          :class="{ active: mode === 'file' }"
          :aria-pressed="mode === 'file'"
          @click="emit('update:mode', 'file')"
        >
          Upload .md
        </button>
      </div>
    </div>

    <div v-if="mode === 'text'" class="input-panel">
      <label class="sr-only" for="markdown-content">AI response in Markdown</label>
      <textarea
        id="markdown-content"
        :value="content"
        maxlength="1048576"
        placeholder="# Your document title\n\nPaste a response from ChatGPT, Claude, DeepSeek, Gemini, or another AI assistant..."
        @input="emit('update:content', ($event.target as HTMLTextAreaElement).value)"
      />
      <p class="input-meta">Markdown, tables, code blocks, Chinese text, and LaTeX formulas are supported.</p>
    </div>

    <div v-else class="upload-panel">
      <input
        id="markdown-file"
        ref="fileInput"
        class="sr-only"
        type="file"
        accept=".md,.markdown,text/markdown"
        @change="selectFile"
      />
      <template v-if="file">
        <div class="file-mark" aria-hidden="true">MD</div>
        <div class="file-info">
          <strong>{{ file.name }}</strong>
          <span>{{ formatBytes(file.size) }}</span>
        </div>
        <button class="quiet-button" type="button" @click="clearFile">Remove</button>
      </template>
      <template v-else>
        <div class="file-mark" aria-hidden="true">MD</div>
        <div>
          <p><strong>Choose a Markdown file</strong></p>
          <p class="muted">.md or .markdown, up to 1 MB</p>
        </div>
        <label class="outline-button" for="markdown-file">Browse files</label>
      </template>
    </div>
  </section>
</template>
