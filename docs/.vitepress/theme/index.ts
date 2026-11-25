import type { Theme } from 'vitepress'
import Layout from './next/NextLayout.vue'
import './styles/vars.css'
import './styles/custom.css'
import './next/next.css'
import AgentFlow from './components/AgentFlow.vue'
import StudioHome from './components/StudioHome.vue'
import WechatCard from './components/WechatCard.vue'
import ArticleHeader from './components/ArticleHeader.vue'
import CodeDemo from './components/CodeDemo.vue'
import KnowledgeMap from './components/KnowledgeMap.vue'
import Quiz from './components/Quiz.vue'
import ResourceCard from './components/ResourceCard.vue'

export default {
  Layout,
  enhanceApp({ app }) {
    app.component('AgentFlow', AgentFlow)
    app.component('StudioHome', StudioHome)
    app.component('WechatCard', WechatCard)
    app.component('ArticleHeader', ArticleHeader)
    app.component('CodeDemo', CodeDemo)
    app.component('KnowledgeMap', KnowledgeMap)
    app.component('Quiz', Quiz)
    app.component('ResourceCard', ResourceCard)
  }
} satisfies Theme
