import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import './styles/vars.css'
import './styles/custom.css'

// 导入自定义组件
import AgentFlow from './components/AgentFlow.vue'
import CodeDemo from './components/CodeDemo.vue'
import Quiz from './components/Quiz.vue'
import ResourceCard from './components/ResourceCard.vue'
import PaginationNav from './components/PaginationNav.vue'

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      // 扩展默认布局
      'home-features-after': () => h('div', { class: 'custom-home-section' }),
      'doc-footer-before': () => h('div', { class: 'custom-footer-section' }),
      'doc-after': () => h(PaginationNav),
    })
  },
  enhanceApp({ app, router, siteData }) {
    // 注册全局组件
    app.component('AgentFlow', AgentFlow)
    app.component('CodeDemo', CodeDemo)
    app.component('Quiz', Quiz)
    app.component('ResourceCard', ResourceCard)
    app.component('PaginationNav', PaginationNav)
    
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