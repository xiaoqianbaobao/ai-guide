<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useData, useRoute, withBase } from 'vitepress'

const { frontmatter } = useData()
const route = useRoute()
const expanded = ref(false)
const trigger = ref<HTMLButtonElement | null>(null)
function closePanel() {
  if (!expanded.value) return
  expanded.value = false
  void nextTick(() => trigger.value?.focus())
}
const isDocument = computed(() => !frontmatter.value.layout || frontmatter.value.layout === 'doc')
watch(() => route.path, () => { expanded.value = false })
</script>

<template>
  <div v-if="isDocument" class="wechat-rail" @keyup.esc="closePanel">
    <div v-if="expanded" id="wechat-rail-panel" class="wechat-rail__panel">
      <div class="wechat-rail__heading"><strong>微信公众号</strong><button type="button" class="wechat-rail__close" aria-label="关闭二维码" @click="closePanel">×</button></div>
      <p>关注公众号，一起交流 AI、产品与创造。</p>
      <a :href="withBase('/wechat-qr.jpg')" target="_blank" rel="noopener" aria-label="打开微信公众号二维码大图"><img :src="withBase('/wechat-qr.jpg')" alt="微信公众号二维码" width="156" height="156"></a>
      <span>微信扫一扫 · 手机可长按识别</span>
    </div>
    <button ref="trigger" type="button" class="wechat-rail__trigger" aria-controls="wechat-rail-panel" :aria-expanded="expanded" @click="expanded = !expanded">
      <svg aria-hidden="true" viewBox="0 0 24 24" fill="none"><path d="M20.5 10.6c0-4.2-3.9-7.6-8.7-7.6S3 6.4 3 10.6c0 2.1 1 4 2.7 5.4l-.7 2.8 3-1.4c1.1.5 2.4.7 3.8.7h.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M21 16.1c0-2.7-2.5-4.9-5.6-4.9s-5.6 2.2-5.6 4.9 2.5 4.9 5.6 4.9c.9 0 1.7-.2 2.5-.5l2 .9-.5-1.8c1-.9 1.6-2.1 1.6-3.5Z" fill="currentColor"/><circle cx="8.8" cy="9.2" r=".9" fill="currentColor"/><circle cx="14.5" cy="9.2" r=".9" fill="currentColor"/></svg>
      <span>公众号</span>
    </button>
  </div>
</template>
