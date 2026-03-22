<script setup lang="ts">
interface Resource {
  title: string
  description: string
  url: string
  type: 'paper' | 'video' | 'tool' | 'course'
  tags?: string[]
}

const props = defineProps<{
  resource: Resource
}>()

const typeColors = {
  paper: 'var(--vp-c-tip-1)',
  video: 'var(--vp-c-warning-1)',
  tool: 'var(--vp-c-success)',
  course: 'var(--vp-c-danger-1)'
}

const typeIcons = {
  paper: '📄',
  video: '▶️',
  tool: '🛠️',
  course: '🎓'
}
</script>

<template>
  <a 
    :href="resource.url" 
    target="_blank"
    class="resource-card"
    rel="noopener noreferrer"
  >
    <div class="card-header">
      <span class="type-badge" :style="{ backgroundColor: typeColors[resource.type] + '20', color: typeColors[resource.type] }">
        {{ typeIcons[resource.type] }} {{ resource.type }}
      </span>
      <span class="external-link">🔗</span>
    </div>
    
    <div class="card-content">
      <h4 class="card-title">{{ resource.title }}</h4>
      <p class="card-description">{{ resource.description }}</p>
      
      <div v-if="resource.tags?.length" class="card-tags">
        <span 
          v-for="tag in resource.tags" 
          :key="tag"
          class="tag"
        >
          {{ tag }}
        </span>
      </div>
    </div>
  </a>
</template>

<style scoped>
.resource-card {
  display: block;
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--vp-border-radius);
  padding: 1.25rem;
  margin-bottom: 1rem;
  background: var(--vp-c-bg);
  color: inherit;
  text-decoration: none;
  transition: all var(--vp-transition-duration);
  overflow: hidden;
}

.resource-card:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: var(--vp-shadow-2);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--vp-c-bg-soft);
}

.external-link {
  font-size: 1.25rem;
  opacity: 0.6;
  transition: opacity var(--vp-transition-duration);
}

.resource-card:hover .external-link {
  opacity: 1;
}

.card-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  line-height: 1.4;
}

.card-description {
  margin: 0 0 1rem 0;
  color: var(--vp-c-text-2);
  line-height: 1.6;
  font-size: 0.95rem;
  flex-grow: 1;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
}

.tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.resource-card:hover .tag {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
}
</style>