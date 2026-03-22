<script setup lang="ts">
import { ref } from 'vue'

interface Option {
  id: string
  text: string
}

const props = defineProps<{
  question: string
  options: Option[]
  correct: string
  explanation?: string
}>()

const selectedOption = ref<string | null>(null)
const showResult = ref(false)

const handleSelect = (optionId: string) => {
  if (!showResult.value) {
    selectedOption.value = optionId
  }
}

const handleSubmit = () => {
  showResult.value = true
}

const isCorrect = () => selectedOption.value === props.correct

const resetQuiz = () => {
  selectedOption.value = null
  showResult.value = false
}
</script>

<template>
  <div class="quiz">
    <div class="quiz-question">
      <h4>{{ question }}</h4>
    </div>
    
    <div class="quiz-options">
      <div
        v-for="option in options"
        :key="option.id"
        class="quiz-option"
        :class="{
          'selected': selectedOption === option.id,
          'correct': showResult && option.id === correct,
          'incorrect': showResult && selectedOption === option.id && option.id !== correct
        }"
        @click="handleSelect(option.id)"
      >
        <span class="option-letter">{{ String.fromCharCode(65 + options.indexOf(option)) }}</span>
        <span class="option-text">{{ option.text }}</span>
      </div>
    </div>

    <div v-if="showResult" class="quiz-result">
      <div :class="`result-message ${isCorrect() ? 'correct' : 'incorrect'}`">
        {{ isCorrect() ? '✅ 回答正确！' : '❌ 回答错误' }}
      </div>
      
      <div v-if="explanation" class="explanation">
        <details>
          <summary>💡 解析</summary>
          <p>{{ explanation }}</p>
        </details>
      </div>
    </div>

    <div class="quiz-actions">
      <button 
        v-if="!showResult"
        class="submit-btn"
        :disabled="!selectedOption"
        @click="handleSubmit"
      >
        提交答案
      </button>
      <button 
        v-else
        class="reset-btn"
        @click="resetQuiz"
      >
        重新答题
      </button>
    </div>
  </div>
</template>

<style scoped>
.quiz {
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--vp-border-radius);
  overflow: hidden;
  margin: 1.5rem 0;
  background: var(--vp-c-bg-soft);
}

.quiz-question {
  padding: 1.5rem;
  border-bottom: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-alt);
}

.quiz-question h4 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--vp-c-text-1);
}

.quiz-options {
  padding: 1rem;
}

.quiz-option {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--vp-border-radius);
  cursor: pointer;
  transition: all var(--vp-transition-duration);
  background: var(--vp-c-bg);
}

.quiz-option:hover {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
}

.quiz-option.selected {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
}

.quiz-option.correct {
  border-color: var(--vp-c-success);
  background: rgba(16, 185, 129, 0.1);
}

.quiz-option.incorrect {
  border-color: var(--vp-c-error);
  background: rgba(239, 68, 68, 0.1);
}

.option-letter {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-2);
  font-weight: 600;
  font-size: 12px;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.quiz-option.selected .option-letter,
.quiz-option.correct .option-letter {
  background: var(--vp-c-brand-1);
  color: white;
}

.quiz-option.correct .option-letter {
  background: var(--vp-c-success);
}

.quiz-option.incorrect .option-letter {
  background: var(--vp-c-error);
}

.quiz-option.correct .option-text {
  color: var(--vp-c-success);
  font-weight: 500;
}

.quiz-option.incorrect .option-text {
  color: var(--vp-c-error);
}

.quiz-result {
  padding: 0 1rem 1rem;
}

.result-message {
  padding: 0.75rem 1rem;
  border-radius: var(--vp-border-radius);
  margin-bottom: 1rem;
  font-weight: 500;
}

.result-message.correct {
  background: rgba(16, 185, 129, 0.1);
  color: var(--vp-c-success);
  border: 1px solid var(--vp-c-success);
}

.result-message.incorrect {
  background: rgba(239, 68, 68, 0.1);
  color: var(--vp-c-error);
  border: 1px solid var(--vp-c-error);
}

.explanation {
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--vp-border-radius);
  padding: 1rem;
}

.explanation summary {
  cursor: pointer;
  font-weight: 500;
  color: var(--vp-c-brand-1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.explanation summary::marker {
  color: var(--vp-c-brand-1);
}

.explanation p {
  margin: 0.5rem 0 0 0;
  color: var(--vp-c-text-2);
  line-height: 1.6;
}

.quiz-actions {
  padding: 0 1rem 1rem;
  display: flex;
  gap: 0.75rem;
}

.submit-btn {
  padding: 0.5rem 1.5rem;
  background: var(--vp-c-brand-1);
  color: white;
  border: none;
  border-radius: var(--vp-border-radius);
  cursor: pointer;
  font-weight: 500;
  transition: background var(--vp-transition-duration);
}

.submit-btn:hover:not(:disabled) {
  background: var(--vp-c-brand-2);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.reset-btn {
  padding: 0.5rem 1.5rem;
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-1);
  border-radius: var(--vp-border-radius);
  cursor: pointer;
  font-weight: 500;
  transition: all var(--vp-transition-duration);
}

.reset-btn:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}
</style>