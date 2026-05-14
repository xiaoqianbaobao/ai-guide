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
        class="article-tag"
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
defineProps<{
  module: string
  tags?: string[]
  readingTime?: string
  prerequisite?: string
  summary?: string
}>()
</script>
