<template>
  <div class="pagination-nav">
    <a v-if="prev" :href="prev.link" class="prev">
      <span class="arrow">←</span>
      <span class="text">{{ prev.text }}</span>
    </a>
    <a v-if="next" :href="next.link" class="next">
      <span class="text">{{ next.text }}</span>
      <span class="arrow">→</span>
    </a>
  </div>
</template>

<script setup>
import { useData } from 'vitepress'

const { frontmatter } = useData()

// 简单的分页逻辑 - 基于文件名排序
const currentPage = frontmatter.value.filePath || ''
const currentLesson = currentPage.match(/lesson-(\d+)/)?.[1]

if (currentLesson) {
  const lessonNum = parseInt(currentLesson)
  const prevLesson = lessonNum > 1 ? `lesson-${String(lessonNum - 1).padStart(2, '0')}` : null
  const nextLesson = lessonNum < 5 ? `lesson-${String(lessonNum + 1).padStart(2, '0')}` : null
  
  if (prevLesson) {
    frontmatter.value.prev = {
      text: `第${lessonNum - 1}期`,
      link: `/models/python-basics/${prevLesson}/`
    }
  }
  
  if (nextLesson) {
    frontmatter.value.next = {
      text: `第${lessonNum + 1}期`,
      link: `/models/python-basics/${nextLesson}/`
    }
  }
}
</script>

<style scoped>
.pagination-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--vp-c-bg-soft);
}

.pagination-nav a {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--vp-c-text-2);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color var(--vp-transition-duration) var(--vp-transition-timing);
}

.pagination-nav a:hover {
  color: var(--vp-c-brand-1);
}

.arrow {
  font-size: 1.2rem;
  font-weight: bold;
}

.prev .arrow {
  order: -1;
}

.next .arrow {
  order: 1;
}

@media (max-width: 640px) {
  .pagination-nav {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>