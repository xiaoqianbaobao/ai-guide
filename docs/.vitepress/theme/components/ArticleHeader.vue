<template>
  <div class="article-header">
    <div class="article-header-top">
      <span class="article-module">{{ module }}</span>
      <span v-if="readingTime" class="article-meta-text">预计阅读：{{ readingTime }}</span>
      <span v-if="prerequisite" class="article-meta-text">前置知识：{{ prerequisite }}</span>
    </div>
    <div v-if="tags?.length" class="article-tags">
      <span
        v-for="tag in tags"
        :key="tag"
        :class="['article-tag', resolveTagClass(tag)]"
      >
        {{ tag }}
      </span>
    </div>
    <p v-if="summary" class="article-summary">
      {{ summary }}
    </p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  module: string
  tags?: string[]
  readingTime?: string
  prerequisite?: string
  summary?: string
}>()

function resolveTagClass(tag: string) {
  if (tag.includes('原理')) return 'is-principle'
  if (tag.includes('核心')) return 'is-core'
  if (tag.includes('实战')) return 'is-practice'
  if (tag.includes('工程')) return 'is-engineering'
  return 'is-default'
}
</script>
