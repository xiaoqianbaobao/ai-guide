<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Content, useData, useRoute, withBase } from 'vitepress'
import WechatRail from '../components/WechatRail.vue'
import type { LessonLink, LessonSidebar } from '../navigation'
import type { SearchDocument } from './search.data'

const { page, frontmatter, theme, isDark } = useData()
const route = useRoute()
const menuOpen = ref(false)
const sidebarOpen = ref(false)
const openDropdown = ref<string | null>(null)
const searchOpen = ref(false)
const query = ref('')
const searchInput = ref<HTMLInputElement | null>(null)
const searchButton = ref<HTMLButtonElement | null>(null)
const documents = ref<SearchDocument[]>([])
const searchLoading = ref(false)
const searchError = ref(false)
async function toggleSearch() {
  searchOpen.value = !searchOpen.value
  if (!searchOpen.value) { searchButton.value?.focus(); return }
  menuOpen.value = false
  sidebarOpen.value = false
  openDropdown.value = null
  await nextTick()
  searchInput.value?.focus()
  if (documents.value.length || searchLoading.value) return
  searchLoading.value = true
  searchError.value = false
  try { documents.value = (await import('./search.data')).data }
  catch { searchError.value = true }
  finally { searchLoading.value = false }
}
function handleShortcut(event: KeyboardEvent) {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    if (!searchOpen.value) void toggleSearch()
    else searchInput.value?.focus()
  }
}
function closePanels() {
  if (searchOpen.value) { searchOpen.value = false; searchButton.value?.focus() }
  menuOpen.value = false
  sidebarOpen.value = false
  openDropdown.value = null
}
function handleOutsideClick(event: PointerEvent) {
  if (!(event.target as Element | null)?.closest('.next-dropdown')) openDropdown.value = null
}
async function copyCode(event: MouseEvent) {
  const button = (event.target as Element | null)?.closest<HTMLButtonElement>('button.copy')
  if (!button) return
  const code = button.parentElement?.querySelector('pre code')?.textContent
  if (code == null) return
  try {
    if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(code)
    else {
      const input = document.createElement('textarea')
      input.value = code
      input.style.cssText = 'position:fixed;opacity:0;pointer-events:none'
      document.body.appendChild(input)
      input.select()
      const copied = document.execCommand('copy')
      input.remove()
      if (!copied) throw new Error('copy failed')
    }
    button.dataset.copyState = 'success'
    button.setAttribute('aria-label', '已复制代码')
  } catch {
    button.dataset.copyState = 'error'
    button.setAttribute('aria-label', '复制失败，请手动复制代码')
  }
  window.setTimeout(() => { delete button.dataset.copyState; button.setAttribute('aria-label', '复制代码') }, 2000)
}
function scrollCodeWithKeyboard(event: KeyboardEvent) {
  const pre = event.target instanceof HTMLElement ? event.target : null
  if (!pre?.matches('div[class*="language-"] > pre[tabindex="0"]')) return
  if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return
  pre.scrollLeft += event.key === 'ArrowRight' ? 48 : -48
  event.preventDefault()
}
const focus = ref(false)
const headings = ref<{ id: string; title: string; level: number }[]>([])
let diagramObserver: MutationObserver | undefined
let codeResizeObserver: ResizeObserver | undefined
function updateCodeScrollability() {
  document.querySelectorAll<HTMLElement>('.next-article div[class*="language-"] > pre').forEach(pre => {
    if (pre.scrollWidth > pre.clientWidth + 1) {
      pre.tabIndex = 0
      pre.setAttribute('aria-label', '代码块，可使用方向键水平滚动')
    } else {
      pre.removeAttribute('tabindex')
      pre.removeAttribute('aria-label')
    }
  })
}
function updateDiagramWidths() {
  document.querySelectorAll<SVGSVGElement>('.next-article .mermaid svg').forEach(svg => {
    const width = svg.viewBox.baseVal.width
    if (width > 0) svg.style.setProperty('--diagram-width', `${Math.ceil(width)}px`)
    const container = svg.closest<HTMLElement>('.mermaid')
    if (container) {
      container.tabIndex = 0
      container.setAttribute('role', 'region')
      container.setAttribute('aria-label', '图表，可左右滚动')
    }
  })
}
async function updateHeadings() {
  await nextTick()
  diagramObserver?.disconnect()
  codeResizeObserver?.disconnect()
  const article = document.querySelector('.next-article')
  if (article) {
    diagramObserver = new MutationObserver(updateDiagramWidths)
    diagramObserver.observe(article, { childList: true, subtree: true })
    updateDiagramWidths()
    if (typeof ResizeObserver !== 'undefined') {
      codeResizeObserver = new ResizeObserver(updateCodeScrollability)
      codeResizeObserver.observe(article)
    }
    updateCodeScrollability()
  }
  document.querySelectorAll<HTMLButtonElement>('.next-article button.copy').forEach(button => {
    button.type = 'button'
    button.title = '复制代码'
    button.setAttribute('aria-label', '复制代码')
  })
  headings.value = Array.from(document.querySelectorAll<HTMLElement>('.next-article h2[id], .next-article h3[id]'))
    .map(heading => ({ id: heading.id, title: heading.textContent?.replace(/^#\s*/, '').trim() || '', level: Number(heading.tagName.slice(1)) }))
    .filter(heading => heading.title)
}
onMounted(() => { void updateHeadings(); window.addEventListener('keydown', handleShortcut); window.addEventListener('resize', updateCodeScrollability); document.addEventListener('pointerdown', handleOutsideClick) })
onBeforeUnmount(() => { diagramObserver?.disconnect(); codeResizeObserver?.disconnect(); window.removeEventListener('keydown', handleShortcut); window.removeEventListener('resize', updateCodeScrollability); document.removeEventListener('pointerdown', handleOutsideClick) })
const home = computed(() => frontmatter.value.layout === 'home')
const sidebar = computed(() => (theme.value.sidebar ?? {}) as LessonSidebar)
const group = computed(() => {
  const pagePath = '/' + page.value.relativePath
  const key = Object.keys(sidebar.value).sort((a, b) => b.length - a.length).find(key => pagePath.startsWith(key))
  return key ? sidebar.value[key] : []
})
const links = computed(() => group.value.flatMap(item => item.items ?? []))
const searchTerms = computed(() => query.value.trim().toLowerCase().split(/\s+/).filter(Boolean))
const searchResults = computed(() => {
  const terms = searchTerms.value
  if (!terms.length) return []
  const phrase = terms.join(' ')
  return documents.value.map((item, index) => {
    const title = item.title.toLowerCase()
    const text = item.text.toLowerCase()
    if (!terms.every(term => title.includes(term) || text.includes(term))) return null
    // Prefer exact title phrases, then title matches; keep source order for ties.
    const score = (title.includes(phrase) ? 100 : 0) +
      terms.filter(term => title.includes(term)).length * 10 + (text.includes(phrase) ? 1 : 0)
    return { item, index, score }
  }).filter((match): match is { item: SearchDocument; index: number; score: number } => match !== null)
    .sort((a, b) => b.score - a.score || a.index - b.index)
    .slice(0, 20).map(match => match.item)
})
function excerpt(item: SearchDocument) {
  const text = item.text.toLowerCase()
  const positions = searchTerms.value.map(term => text.indexOf(term)).filter(index => index >= 0)
  const i = positions.length ? Math.min(...positions) : -1
  return i < 0 ? item.text.slice(0, 100) : item.text.slice(Math.max(0, i - 30), i + 90)
}
function href(path: string) { return withBase(path) }
function active(path: string) {
  const normalized = (s: string) => s.replace(/(?:\/index)?\.md$/, '').replace(/\/$/, '')
  return normalized('/' + page.value.relativePath) === normalized(path)
}
const prev = computed(() => frontmatter.value.prev as LessonLink | false)
const next = computed(() => frontmatter.value.next as LessonLink | false)
watch(() => route.path, () => { menuOpen.value = false; sidebarOpen.value = false; openDropdown.value = null; searchOpen.value = false; void updateHeadings() }, { flush: 'post' })
</script>

<template>
  <div class="next-app" @keyup.esc="closePanels">
    <a class="next-skip" href="#main">跳到正文</a>
    <header class="next-header">
      <a class="next-brand" :href="href('/')"><img :src="href('/logo.svg')" width="30" height="30" alt=""> <strong>造与见</strong></a>
      <nav id="site-navigation" class="next-topnav" :class="{ 'is-open': menuOpen }" aria-label="主导航">
        <template v-for="item in theme.nav" :key="item.text">
          <a v-if="item.link" :href="href(item.link)">{{ item.text }}</a>
          <div v-else class="next-dropdown"><button type="button" class="next-dropdown-trigger" :aria-expanded="openDropdown === item.text" @click="openDropdown = openDropdown === item.text ? null : item.text">{{ item.text }} <span aria-hidden="true">⌄</span></button><div v-if="openDropdown === item.text" class="next-dropdown-panel"><a v-for="child in item.items" :key="child.link" :href="href(child.link)">{{ child.text }}</a></div></div>
        </template>
      </nav>
      <div class="next-header-actions"><button ref="searchButton" type="button" @click="toggleSearch" :aria-expanded="searchOpen" aria-keyshortcuts="Control+K Meta+K">搜索</button><button type="button" @click="isDark = !isDark" :aria-label="isDark ? '切换浅色模式' : '切换深色模式'">{{ isDark ? '☼' : '☾' }}</button><button class="next-mobile-menu" type="button" :aria-expanded="menuOpen" aria-controls="site-navigation" @click="menuOpen = !menuOpen; sidebarOpen = false; openDropdown = null; searchOpen = false">导航</button><button v-if="!home && group.length" class="next-mobile-lessons" type="button" :aria-expanded="sidebarOpen" aria-controls="lesson-navigation" @click="sidebarOpen = !sidebarOpen; focus = false; menuOpen = false; openDropdown = null; searchOpen = false">课程</button></div>
    </header>
    <div v-if="searchOpen" class="next-search" role="search"><label for="next-search-input">搜索文章全文</label><input id="next-search-input" ref="searchInput" v-model="query" type="search" placeholder="输入关键词，用空格分隔"><p v-if="!query.trim()">输入关键词查找文章</p><p v-else-if="searchLoading">正在加载搜索索引…</p><p v-else-if="searchError">搜索索引加载失败，请关闭后重试。</p><p v-else-if="!searchResults.length">没有找到匹配的文章</p><a v-for="item in searchResults" :key="item.url" :href="href(item.url)"><strong>{{ item.title }}</strong><small>{{ excerpt(item) }}</small></a></div>
    <main v-if="home" id="main" class="next-home"><Content /></main>
    <div v-else class="next-layout" :class="{ 'is-focus': focus, 'is-menu-open': sidebarOpen }">
      <aside id="lesson-navigation" class="next-sidebar" aria-label="课程目录"><section v-for="part in group" :key="part.text"><h2>{{ part.text }}</h2><a v-for="item in part.items" :key="item.link" :href="href(item.link)" :aria-current="active(item.link) ? 'page' : undefined">{{ item.text }}</a></section></aside>
      <main id="main" class="next-main"><article class="next-article vp-doc" @click="copyCode" @keydown="scrollCodeWithKeyboard"><button type="button" class="next-focus" :aria-pressed="focus" @click="focus = !focus">{{ focus ? '退出专注' : '专注阅读' }}</button><Content /><nav v-if="prev || next" class="prev-next" aria-label="课程分页"><a v-if="prev" class="pager-link prev" :href="href(prev.link)"><small>本专题上一篇</small><strong>{{ prev.text }}</strong></a><a v-if="next" class="pager-link next" :href="href(next.link)"><small>本专题下一篇</small><strong>{{ next.text }}</strong></a></nav></article></main>
      <aside v-if="headings.length" class="next-outline" aria-label="本文目录"><strong>本文目录</strong><a v-for="heading in headings" :key="heading.id" :class="{ sub: heading.level > 2 }" :href="'#' + encodeURIComponent(heading.id)">{{ heading.title }}</a></aside>
    </div>
    <footer class="next-footer">造与见 · 从想法到第一个真实客户</footer><WechatRail v-if="!home" />
  </div>
</template>
