import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import NextLayout from './next/NextLayout.vue'
import './next/next.css'
import { h } from 'vue'
import './styles/vars.css'
import './styles/custom.css'

// 导入自定义组件
import AgentFlow from './components/AgentFlow.vue'
import StudioHome from './components/StudioHome.vue'
import WechatCard from './components/WechatCard.vue'
import WechatRail from './components/WechatRail.vue'
import ArticleHeader from './components/ArticleHeader.vue'
import CodeDemo from './components/CodeDemo.vue'
import KnowledgeMap from './components/KnowledgeMap.vue'
import Quiz from './components/Quiz.vue'
import ResourceCard from './components/ResourceCard.vue'
import ReadingModeToggle from './components/ReadingModeToggle.vue'

export default {
  extends: DefaultTheme,
  Layout: import.meta.env.VITE_NEXT_LAYOUT === '1' ? NextLayout : () => {
    return h(DefaultTheme.Layout, null, {
      // 扩展默认布局
      'home-features-after': () => h('div', { class: 'custom-home-section' }),
      'layout-bottom': () => h(WechatRail),
      'doc-before': () => h(ReadingModeToggle),
    })
  },
  enhanceApp({ app, router, siteData }) {
    // 注册全局组件
    app.component('AgentFlow', AgentFlow)
    app.component('StudioHome', StudioHome)
    app.component('WechatCard', WechatCard)
    app.component('ArticleHeader', ArticleHeader)
    app.component('CodeDemo', CodeDemo)
    app.component('KnowledgeMap', KnowledgeMap)
    app.component('Quiz', Quiz)
    app.component('ResourceCard', ResourceCard)
    app.component('ReadingModeToggle', ReadingModeToggle)
    
    // 全局属性
    app.config.globalProperties.$site = siteData
    
    // 路由守卫：页面切换埋点
    router.onAfterRouteChanged = (to) => {
      if (typeof window !== 'undefined' && window.umami) {
        window.umami.track('page_view', { path: to })
      }
    }
  }
} satisfies Theme
