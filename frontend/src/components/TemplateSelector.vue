<script setup lang="ts">
import type { TemplateName } from '../api/types'

defineProps<{ modelValue: TemplateName }>()
const emit = defineEmits<{ 'update:modelValue': [value: TemplateName] }>()

const templates: Array<{ name: TemplateName; label: string; description: string; accent: string }> = [
  {
    name: 'academic',
    label: 'Academic',
    description: 'Research papers and scholarly reports',
    accent: 'A',
  },
  {
    name: 'report',
    label: 'Report',
    description: 'Business briefs and professional reports',
    accent: 'R',
  },
  {
    name: 'notes',
    label: 'Notes',
    description: 'Learning notes and compact references',
    accent: 'N',
  },
]
</script>

<template>
  <fieldset aria-labelledby="template-heading">
    <div class="section-heading">
      <div>
        <p class="step-label">Step 02</p>
        <legend id="template-heading">Choose a document style</legend>
      </div>
    </div>
    <div class="template-grid">
      <label
        v-for="item in templates"
        :key="item.name"
        class="template-card"
        :class="{ selected: modelValue === item.name }"
      >
        <input
          type="radio"
          name="template"
          :value="item.name"
          :checked="modelValue === item.name"
          @change="emit('update:modelValue', item.name)"
        />
        <span class="template-letter" aria-hidden="true">{{ item.accent }}</span>
        <span class="template-copy">
          <strong>{{ item.label }}</strong>
          <small>{{ item.description }}</small>
        </span>
        <span class="radio-mark" aria-hidden="true"></span>
      </label>
    </div>
  </fieldset>
</template>
