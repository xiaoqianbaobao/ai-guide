<template>
  <div class="reading-mode-toggle">
    <button
      type="button"
      class="toggle-button"
      :aria-pressed="sidebarHidden"
      @click="toggleSidebar"
    >
      {{ sidebarHidden ? '显示目录' : '隐藏目录' }}
    </button>
    <button
      type="button"
      class="toggle-button"
      :aria-pressed="focusMode"
      @click="toggleFocus"
    >
      {{ focusMode ? '退出专注' : '专注阅读' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const STORAGE_KEY = 'ai-guide-reading-mode'
const sidebarHidden = ref(false)
const focusMode = ref(false)

function applyState() {
  if (typeof document === 'undefined') {
    return
  }

  const root = document.documentElement
  root.classList.toggle('reading-sidebar-hidden', sidebarHidden.value)
  root.classList.toggle('reading-focus-mode', focusMode.value)
}

function saveState() {
  if (typeof window === 'undefined') {
    return
  }

  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      sidebarHidden: sidebarHidden.value,
      focusMode: focusMode.value
    })
  )
}

function toggleSidebar() {
  const nextValue = !sidebarHidden.value
  sidebarHidden.value = nextValue

  // 专注阅读默认依赖隐藏侧边栏，手动展开目录时退出专注模式。
  if (!nextValue && focusMode.value) {
    focusMode.value = false
  }
}

function toggleFocus() {
  const nextValue = !focusMode.value
  focusMode.value = nextValue

  if (nextValue) {
    sidebarHidden.value = true
  }
}

watch([sidebarHidden, focusMode], () => {
  applyState()
  saveState()
})

onMounted(() => {
  if (typeof window !== 'undefined') {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (raw) {
      try {
        const saved = JSON.parse(raw)
        sidebarHidden.value = Boolean(saved.sidebarHidden)
        focusMode.value = Boolean(saved.focusMode)
      } catch {
        window.localStorage.removeItem(STORAGE_KEY)
      }
    }
  }

  applyState()
})

onBeforeUnmount(() => {
  if (typeof document === 'undefined') {
    return
  }

  const root = document.documentElement
  root.classList.remove('reading-sidebar-hidden', 'reading-focus-mode')
})
</script>

<style scoped>
.reading-mode-toggle {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 0 0 1.25rem;
}

.toggle-button {
  appearance: none;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: var(--vp-c-bg-elv);
  color: var(--vp-c-text-1);
  border-radius: 999px;
  padding: 0.45rem 0.9rem;
  font-size: 0.9rem;
  line-height: 1;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.toggle-button:hover,
.toggle-button[aria-pressed='true'] {
  background: var(--vp-c-brand-soft);
  border-color: rgba(0, 0, 0, 0.12);
}

:global(.dark) .toggle-button {
  border-color: rgba(255, 255, 255, 0.1);
}

:global(.dark) .toggle-button:hover,
:global(.dark) .toggle-button[aria-pressed='true'] {
  border-color: rgba(255, 255, 255, 0.16);
}

@media (max-width: 768px) {
  .reading-mode-toggle {
    display: none;
  }
}
</style>
