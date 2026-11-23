<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Content, useData, useRoute, withBase } from 'vitepress'
import WechatRail from '../components/WechatRail.vue'
import type { LessonLink, LessonSidebar } from '../navigation'
import type { SearchDocument } from './search.data'

const { page, frontmatter, theme, isDark } = useData()
const route = useRoute()
const menuOpen = ref(false)
const searchOpen = ref(false)
const query = ref('')
const documents = ref<SearchDocument[]>([])
const searchLoading = ref(false)
const searchError = ref(false)
async function toggleSearch() {
  searchOpen.value = !searchOpen.value
  if (!searchOpen.value || documents.value.length || searchLoading.value) return
  searchLoading.value = true
  searchError.value = false
  try { documents.value = (await import('./search.data')).data }
  catch { searchError.value = true }
  finally { searchLoading.value = false }
}
const focus = ref(false)
const home = computed(() => frontmatter.value.layout === 'home')
const sidebar = computed(() => (theme.value.sidebar ?? {}) as LessonSidebar)
const group = computed(() => {
  const pagePath = '/' + page.value.relativePath
  const key = Object.keys(sidebar.value).sort((a, b) => b.length - a.length).find(key => pagePath.startsWith(key))
  return key ? sidebar.value[key] : []
})
const links = computed(() => group.value.flatMap(item => item.items ?? []))
const searchResults = computed(() => {
  const term = query.value.trim().toLowerCase()
  if (!term) return []
  return documents.value.filter(item => (item.title + ' ' + item.text).toLowerCase().includes(term)).slice(0, 20)
})
function excerpt(item: SearchDocument) {
  const i = item.text.toLowerCase().indexOf(query.value.trim().toLowerCase())
  return i < 0 ? item.text.slice(0, 100) : item.text.slice(Math.max(0, i - 30), i + 90)
}
function href(path: string) { return withBase(path) }
function active(path: string) {
  const normalized = (s: string) => s.replace(/(?:\/index)?\.md$/, '').replace(/\/$/, '')
  return normalized('/' + page.value.relativePath) === normalized(path)
}
const prev = computed(() => frontmatter.value.prev as LessonLink | false)
const next = computed(() => frontmatter.value.next as LessonLink | false)
watch(() => route.path, () => { menuOpen.value = false; searchOpen.value = false })
</script>

<template>
  <div class="next-app" @keyup.esc="searchOpen = false; menuOpen = false">
    <a class="next-skip" href="#main">跳到正文</a>
    <header class="next-header">
      <a class="next-brand" :href="href('/')"><img :src="href('/logo.svg')" width="30" height="30" alt=""> <strong>造与见</strong></a>
      <nav class="next-topnav" :class="{ 'is-open': menuOpen }" aria-label="主导航">
        <template v-for="item in theme.nav" :key="item.text">
          <a v-if="item.link" :href="href(item.link)">{{ item.text }}</a>
          <details v-else class="next-dropdown"><summary>{{ item.text }}</summary><div><a v-for="child in item.items" :key="child.link" :href="href(child.link)">{{ child.text }}</a></div></details>
        </template>
      </nav>
      <div class="next-header-actions"><button type="button" @click="toggleSearch" :aria-expanded="searchOpen">搜索</button><button type="button" @click="isDark = !isDark" :aria-label="isDark ? '切换浅色模式' : '切换深色模式'">{{ isDark ? '☼' : '☾' }}</button><button class="next-mobile-menu" type="button" :aria-expanded="menuOpen" @click="menuOpen = !menuOpen">目录</button></div>
    </header>
    <div v-if="searchOpen" class="next-search" role="search"><label for="next-search-input">搜索文章全文</label><input id="next-search-input" v-model="query" type="search" placeholder="输入关键词"><p v-if="!query">输入关键词查找文章</p><p v-else-if="searchLoading">正在加载搜索索引…</p><p v-else-if="searchError">搜索索引加载失败，请关闭后重试。</p><p v-else-if="!searchResults.length">没有找到匹配的文章</p><a v-for="item in searchResults" :key="item.url" :href="href(item.url)"><strong>{{ item.title }}</strong><small>{{ excerpt(item) }}</small></a></div>
    <main v-if="home" id="main" class="next-home"><Content /></main>
    <div v-else class="next-layout" :class="{ 'is-focus': focus, 'is-menu-open': menuOpen }">
      <aside class="next-sidebar" aria-label="课程目录"><section v-for="part in group" :key="part.text"><h2>{{ part.text }}</h2><a v-for="item in part.items" :key="item.link" :href="href(item.link)" :aria-current="active(item.link) ? 'page' : undefined">{{ item.text }}</a></section></aside>
      <main id="main" class="next-main"><article class="next-article vp-doc"><button type="button" class="next-focus" :aria-pressed="focus" @click="focus = !focus">{{ focus ? '退出专注' : '专注阅读' }}</button><Content /><nav v-if="prev || next" class="prev-next" aria-label="课程分页"><a v-if="prev" class="pager-link prev" :href="href(prev.link)"><small>本专题上一篇</small><strong>{{ prev.text }}</strong></a><a v-if="next" class="pager-link next" :href="href(next.link)"><small>本专题下一篇</small><strong>{{ next.text }}</strong></a></nav></article></main>
      <aside v-if="page.headers?.length" class="next-outline" aria-label="本文目录"><strong>本文目录</strong><a v-for="header in page.headers" :key="header.slug" :class="{ sub: header.level > 2 }" :href="'#' + header.slug">{{ header.title }}</a></aside>
    </div>
    <footer class="next-footer">造与见 · 从想法到第一个真实客户</footer><WechatRail v-if="!home" />
  </div>
</template>
