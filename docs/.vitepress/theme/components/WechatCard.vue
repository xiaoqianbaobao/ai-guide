<script setup lang="ts">
import { withBase } from 'vitepress'
defineProps<{ compact?: boolean }>()
</script>
<template>
  <aside class="wechat-card" :class="{ 'wechat-card--compact': compact }" aria-label="关注微信公众号">
    <div class="wechat-card__copy">
      <span class="wechat-card__eyebrow">WECHAT / 持续学习</span>
      <h2>一起把知识变成行动。</h2>
      <p>关注公众号，继续交流 AI、产品与创造的实践。网站中的体系化教程可直接阅读。</p>
      <span class="wechat-card__hint">微信扫一扫 · 手机可长按识别</span>
    </div>
    <a class="wechat-card__qr" :href="withBase('/wechat-qr.jpg')" target="_blank" rel="noopener" aria-label="打开微信公众号二维码大图"><img :src="withBase('/wechat-qr.jpg')" alt="微信公众号二维码，微信扫一扫或长按识别" width="144" height="144" loading="lazy"></a>
  </aside>
</template>
