<template>
  <div class="knowledge-map">
    <div class="knowledge-map-label">你现在在这里</div>
    <div class="knowledge-map-track">
      <template v-for="(item, index) in modules" :key="item.id">
        <a
          :href="withBase(item.link)"
          :class="[
            'knowledge-map-item',
            item.id === currentModule ? 'is-current' : 'is-other'
          ]"
        >
          {{ item.name }}
        </a>
        <span v-if="index < modules.length - 1" class="knowledge-map-separator">
          →
        </span>
      </template>
    </div>
    <p v-if="currentArticle" class="knowledge-map-current">
      当前阅读：{{ currentArticle }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { withBase } from 'vitepress'

interface ModuleItem {
  id: string
  name: string
  link: string
}

defineProps<{
  currentModule: string
  currentArticle?: string
}>()

const modules: ModuleItem[] = [
  { id: 'preface', name: '序章', link: '/00-preface/' },
  { id: 'llm', name: '语言模型基础', link: '/01-llm-foundations/' },
  { id: 'agent', name: 'Agent 核心', link: '/02-agent-core/' },
  { id: 'memory', name: 'Memory 体系', link: '/03-memory/' },
  { id: 'multi-agent', name: '多 Agent', link: '/04-multi-agent/' },
  { id: 'tools', name: '工具与框架', link: '/05-tools-frameworks/' },
  { id: 'eval', name: '评估与进化', link: '/06-eval-evolution/' },
  { id: 'ontology', name: '本体论与知识表示', link: '/07-ontology/' },
  { id: 'self-evolving-skills', name: '自进化 Skills', link: '/08-self-evolving-skills/' },
  { id: 'data-governance', name: '数据治理', link: '/09-data-governance/' },
  { id: 'cases', name: '实战案例', link: '/agent/' }
]
</script>
