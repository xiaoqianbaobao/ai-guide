<script setup lang="ts">
import { ref, computed } from 'vue'

interface FlowStep {
  id: string
  name: string
  desc: string
  details?: string[]
}

const props = defineProps<{
  steps: FlowStep[]
  interactive?: boolean
}>()

const activeStep = ref(0)
const showDetails = ref(false)

const currentStep = computed(() => props.steps[activeStep.value])

const nextStep = () => {
  if (activeStep.value < props.steps.length - 1) {
    activeStep.value++
  }
}

const prevStep = () => {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

const jumpToStep = (index: number) => {
  activeStep.value = index
  showDetails.value = true
}
</script>

<template>
  <div class="agent-flow">
    <div class="flow-steps">
      <div
        v-for="(step, index) in steps"
        :key="step.id"
        class="step-indicator"
        :class="{ 
          'step-active': index === activeStep,
          'step-completed': index < activeStep 
        }"
        @click="jumpToStep(index)"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-title">{{ step.name }}</div>
        <div v-if="index < steps.length - 1" class="step-connector" />
      </div>
    </div>

    <div class="flow-content">
      <div class="content-header">
        <h4>{{ currentStep.name }}</h4>
        <span class="step-badge">Step {{ activeStep + 1 }}/{{ steps.length }}</span>
      </div>
      
      <p class="content-desc">{{ currentStep.desc }}</p>
      
      <div v-if="currentStep.details?.length" class="content-details">
        <button class="toggle-btn" @click="showDetails = !showDetails">
          {{ showDetails ? '收起详情' : '查看详情' }}
        </button>
        
        <div v-show="showDetails" class="details-list">
          <div v-for="(detail, idx) in currentStep.details" :key="idx" class="detail-item">
            <span class="detail-bullet">▸</span>
            {{ detail }}
          </div>
        </div>
      </div>

      <div v-if="interactive" class="flow-controls">
        <button 
          class="control-btn prev" 
          :disabled="activeStep === 0"
          @click="prevStep"
        >
          ← 上一步
        </button>
        <button 
          class="control-btn next" 
          :disabled="activeStep === steps.length - 1"
          @click="nextStep"
        >
          下一步 →
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.agent-flow {
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--vp-border-radius);
  overflow: hidden;
  margin: 1.5rem 0;
  background: var(--vp-c-bg-soft);
}

.flow-steps {
  display: flex;
  padding: 1rem;
  background: var(--vp-c-bg-alt);
  border-bottom: 1px solid var(--vp-c-divider);
  overflow-x: auto;
  gap: 0.5rem;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  position: relative;
  padding: 0.5rem;
  border-radius: var(--vp-border-radius);
  transition: background var(--vp-transition-duration);
  min-width: 80px;
}

.step-indicator:hover {
  background: var(--vp-c-bg-soft);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--vp-c-default-soft);
  color: var(--vp-c-text-2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  transition: all var(--vp-transition-duration);
}

.step-active .step-number {
  background: var(--vp-c-brand-1);
  color: white;
  transform: scale(1.1);
}

.step-completed .step-number {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
}

.step-title {
  margin-top: 0.5rem;
  font-size: 12px;
  color: var(--vp-c-text-2);
  text-align: center;
  white-space: nowrap;
}

.step-active .step-title {
  color: var(--vp-c-brand-1);
  font-weight: 500;
}

.step-connector {
  position: absolute;
  right: -1rem;
  top: 50%;
  width: 1rem;
  height: 2px;
  background: var(--vp-c-divider);
  transform: translateY(-50%);
}

.step-completed + .step-indicator .step-connector {
  background: var(--vp-c-brand-1);
}

.flow-content {
  padding: 1.5rem;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.content-header h4 {
  margin: 0;
  color: var(--vp-c-text-1);
}

.step-badge {
  font-size: 12px;
  padding: 0.25rem 0.75rem;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  border-radius: 9999px;
  font-weight: 500;
}

.content-desc {
  color: var(--vp-c-text-2);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.toggle-btn {
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-2);
  padding: 0.5rem 1rem;
  border-radius: var(--vp-border-radius);
  cursor: pointer;
  font-size: 14px;
  transition: all var(--vp-transition-duration);
}

.toggle-btn:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.details-list {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--vp-c-bg);
  border-radius: var(--vp-border-radius);
  border: 1px solid var(--vp-c-divider);
}

.detail-item {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem 0;
  color: var(--vp-c-text-2);
  font-size: 14px;
}

.detail-bullet {
  color: var(--vp-c-brand-1);
  font-weight: bold;
}

.flow-controls {
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--vp-c-divider);
}

.control-btn {
  padding: 0.5rem 1.5rem;
  border-radius: var(--vp-border-radius);
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all var(--vp-transition-duration);
}

.control-btn.prev {
  background: var(--vp-c-bg-alt);
  color: var(--vp-c-text-1);
}

.control-btn.prev:hover:not(:disabled) {
  background: var(--vp-c-bg-soft);
}

.control-btn.next {
  background: var(--vp-c-brand-1);
  color: white;
}

.control-btn.next:hover:not(:disabled) {
  background: var(--vp-c-brand-2);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>