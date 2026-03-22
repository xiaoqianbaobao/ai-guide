<script setup lang="ts">
import { ref, computed } from 'vue'

interface DemoTab {
  name: string
  lang: string
  code: string
  runnable?: boolean
}

const props = defineProps<{
  tabs: DemoTab[]
  title?: string
  description?: string
  height?: string
}>()

const activeTab = ref(0)
const output = ref('')
const isRunning = ref(false)

const currentTab = computed(() => props.tabs[activeTab.value])

const copyCode = async () => {
  await navigator.clipboard.writeText(currentTab.value.code)
  // 显示复制成功提示
}

const runCode = async () => {
  if (!currentTab.value.runnable) return
  
  isRunning.value = true
  output.value = '运行中...'
  
  try {
    await new Promise(r => setTimeout(r, 1000))
    output.value = '执行结果：\nHello, AI Guide!\n运行时间: 0.023s'
  } catch (e) {
    output.value = `错误: ${e.message}`
  } finally {
    isRunning.value = false
  }
}

const resetCode = () => {
  output.value = ''
}
</script>

<template>
  <div class="code-demo">
    <div v-if="title" class="demo-header">
      <h4>{{ title }}</h4>
      <span v-if="description" class="demo-desc">{{ description }}</span>
    </div>

    <div class="demo-tabs">
      <button
        v-for="(tab, index) in tabs"
        :key="index"
        class="tab-btn"
        :class="{ active: index === activeTab }"
        @click="activeTab = index"
      >
        {{ tab.name }}
      </button>
      
      <div class="tab-actions">
        <button class="action-btn" @click="copyCode" title="复制代码">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
            <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
          </svg>
        </button>
      </div>
    </div>

    <div class="code-editor" :style="{ height: height || '200px' }">
      <pre><code :class="`language-${currentTab.lang}`">{{ currentTab.code }}</code></pre>
    </div>

    <div v-if="currentTab.runnable" class="demo-controls">
      <button 
        class="run-btn" 
        :disabled="isRunning"
        @click="runCode"
      >
        <span v-if="isRunning">▶ 运行中...</span>
        <span v-else>▶ 运行代码</span>
      </button>
      <button class="reset-btn" @click="resetCode">重置</button>
    </div>

    <div v-if="output" class="output-panel">
      <div class="output-header">输出</div>
      <pre class="output-content">{{ output }}</pre>
    </div>
  </div>
</template>

<style scoped>
.code-demo {
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--vp-border-radius);
  overflow: hidden;
  margin: 1.5rem 0;
  background: var(--vp-c-bg);
}

demo-header {
  padding: 1rem;
  background: var(--vp-c-bg-soft);
  border-bottom: 1px solid var(--vp-c-divider);
}

demo-header h4 {
  margin: 0 0 0.25rem 0;
  font-size: 16px;
}

demo-desc {
  font-size: 14px;
  color: var(--vp-c-text-2);
}

demo-tabs {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background: var(--vp-c-bg-alt);
  border-bottom: 1px solid var(--vp-c-divider);
  gap: 0.25rem;
}

tab-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: var(--vp-c-text-2);
  cursor: pointer;
  border-radius: var(--vp-border-radius);
  font-size: 14px;
  transition: all var(--vp-transition-duration);
}

tab-btn:hover {
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-soft);
}

tab-btn.active {
  color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
  font-weight: 500;
}

tab-actions {
  margin-left: auto;
  display: flex;
  gap: 0.5rem;
}

action-btn {
  padding: 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: var(--vp-border-radius);
  color: var(--vp-c-text-2);
}

action-btn:hover {
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
}

code-editor {
  background: #1e1e1e;
  overflow: auto;
}

code-editor pre {
  margin: 0;
  padding: 1rem;
  font-family: var(--vp-font-family-mono);
  font-size: 14px;
  line-height: 1.6;
  color: #d4d4d4;
}

demo-controls {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--vp-c-bg-soft);
  border-top: 1px solid var(--vp-c-divider);
}

run-btn {
  padding: 0.5rem 1.25rem;
  background: var(--vp-c-brand-1);
  color: white;
  border: none;
  border-radius: var(--vp-border-radius);
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

run-btn:hover:not(:disabled) {
  background: var(--vp-c-brand-2);
}

run-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

reset-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-2);
  border-radius: var(--vp-border-radius);
  cursor: pointer;
}

reset-btn:hover {
  border-color: var(--vp-c-text-1);
  color: var(--vp-c-text-1);
}

output-panel {
  border-top: 1px solid var(--vp-c-divider);
  background: #0f172a;
}

output-header {
  padding: 0.5rem 1rem;
  font-size: 12px;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--vp-c-divider);
}

output-content {
  margin: 0;
  padding: 1rem;
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  line-height: 1.5;
  color: #4ade80;
  overflow-x: auto;
}
</style>