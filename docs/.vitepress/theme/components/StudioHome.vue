<script setup lang="ts">
import { withBase } from 'vitepress'
const href = (path: string) => withBase(path)
const stages = [
  ['01', '发现问题', '走进具体场景，找到值得解决的痛点。', '/10-product-fde/customer-discovery'],
  ['02', '验证需求', '用访谈、现有替代方案和试点筛选假设。', '/10-product-fde/customer-discovery'],
  ['03', '做出产品', '用工程、AI 与评估，交付可运行方案。', '/agent/cases/enterprise-agent-roadmap'],
  ['04', '真实使用', '让真实用户参与，观察行为与反馈。', '/10-product-fde/pilot-to-first-customer'],
  ['05', '争取成交', '计算价值、讨论报价，形成可交付合作。', '/10-product-fde/pilot-to-first-customer']
]
</script>
<template>
  <main class="studio">
    <section class="studio-hero wrap">
      <div class="hero-copy">
        <p class="eyebrow"><span></span> AI × 创造 × 商业</p>
        <h1>从想法到<br><em>第一个真实客户。</em></h1>
        <p class="hero-intro">借助 AI，融合 <strong>Builder</strong> 的创造力与 <strong>Seller</strong> 的洞察力。理解问题，做出产品，让价值走进真实世界。</p>
        <div class="hero-actions"><a class="btn primary" :href="href('/guide/idea-to-customer')">开始这段旅程 <span>↗</span></a><a class="btn secondary" href="#knowledge">探索知识地图 <span>↓</span></a></div>
        <p class="hero-note">开源知识体系 · 从 Agent 出发 · 面向所有创造者</p>
      </div>
      <div class="hero-art" aria-label="从想法到客户的学习旅程示意">
        <div class="art-top"><span>THE CREATION JOURNEY</span><span>造与见 / 01</span></div>
        <div class="art-orbit orbit-one"></div><div class="art-orbit orbit-two"></div>
        <div class="art-center"><span>IDEA</span><b>↗</b><span>IMPACT</span></div>
        <div class="art-label art-build"><small>01 / BUILD</small><strong>创造</strong><span>把想法做出来</span></div>
        <div class="art-label art-sell"><small>02 / SELL</small><strong>连接</strong><span>让价值被看见</span></div>
        <div class="art-bottom"><span>LEARN BY DOING</span><span>从 0 到 1，然后持续迭代 →</span></div>
      </div>
    </section>
    <section class="manifesto"><div class="wrap manifesto-inner"><span>OUR BELIEF / 我们相信</span><p>未来属于既能<strong>理解人</strong>，<br>又能<strong>创造解决方案</strong>的人。</p><p>技术让想法成为可能。对人的理解，让它真正有用。这里用系统知识和真实练习，把两者连接起来。</p></div></section>
    <section class="wrap section journey"><div class="section-heading"><div><p class="eyebrow">THE PATH / 学习路径</p><h2>从想法，走向真实世界。</h2></div><p>不是一串孤立的课程，而是一条不断获得证据、做出选择、交付价值的路。</p></div><div class="stage-grid"><a v-for="s in stages" :key="s[0]" :href="href(s[3])" class="stage"><span class="stage-no">{{ s[0] }} <i>↗</i></span><h3>{{ s[1] }}</h3><p>{{ s[2] }}</p></a></div><a class="text-link" :href="href('/guide/idea-to-customer')">查看完整路线与每一步的交付物 →</a></section>
    <section class="abilities"><div class="wrap section"><div class="section-heading"><div><p class="eyebrow">TWO CAPABILITIES / 两种能力</p><h2>会创造，也会连接。</h2></div><p>你不需要先定义自己是哪一种人。让两种能力在同一个项目里互相生长。</p></div><div class="ability-grid"><article class="ability build"><div class="ability-num">01 / BUILDER <span>↗</span></div><h3>把问题<br>变成产品。</h3><p>从模型原理到 Agent、系统架构与评估，学习构建可靠的解决方案。</p><a :href="href('/guide/')">进入技术知识体系 →</a></article><article class="ability sell"><div class="ability-num">02 / SELLER <span>↗</span></div><h3>让价值<br>抵达客户。</h3><p>学习客户访谈、价值验证与企业交付，让好的解决方案被理解、使用和购买。</p><a :href="href('/10-product-fde/')">进入产品与商业化 →</a></article></div></div></section>
    <section id="knowledge" class="wrap section"><div class="section-heading"><div><p class="eyebrow">KNOWLEDGE MAP / 知识地图</p><h2>找到你的起点。</h2></div><p>三种视角，共享一套知识。先从眼前的问题出发，再按需深入。</p></div><div class="entry-grid"><a :href="href('/guide/')"><span>01 / 技术创造者 ↗</span><h3>AI 技术体系</h3><p>模型、Agent、记忆、工程架构与评估。从原理到可运行系统。</p><b>探索技术体系 →</b></a><a :href="href('/10-product-fde/customer-discovery')"><span>02 / 所有创造者 ↗</span><h3>创造与商业化</h3><p>从客户的问题出发，练习访谈、验证、试点与价值沟通。</p><b>从发现问题开始 →</b></a><a :href="href('/agent/cases/enterprise-agent-roadmap')"><span>03 / 企业团队 ↗</span><h3>企业实践</h3><p>了解企业 Agent 的治理、评估与交付路线。团队课程正在规划。</p><b>查看企业实战路线 →</b></a></div></section>
    <section class="featured"><div class="wrap section"><div class="section-heading"><div><p class="eyebrow">START READING / 精选内容</p><h2>从一篇文章开始。</h2></div><p>理论要能指导行动。每个主题都尽量回到具体问题、取舍与练习。</p></div><div class="reading-list"><a :href="href('/10-product-fde/customer-discovery')"><span>SELLER / 01</span><strong>客户访谈：找到一个值得解决的问题</strong><i>↗</i></a><a :href="href('/10-product-fde/pilot-to-first-customer')"><span>SELLER / 02</span><strong>从试点到第一个客户：如何验证价值</strong><i>↗</i></a><a :href="href('/agent/cases/enterprise-agent-roadmap')"><span>BUILDER / 01</span><strong>企业级 Agent：从知识助手到可治理工作流</strong><i>↗</i></a><a :href="href('/03-memory/wiki-and-runtime-context')"><span>BUILDER / 02</span><strong>知识、记忆与上下文：各自负责什么</strong><i>↗</i></a></div></div></section>
    <div class="wrap studio-wechat"><WechatCard /></div>
    <section class="wrap closing"><p class="eyebrow">KEEP BUILDING, KEEP LEARNING</p><h2>从一个真实的问题开始。</h2><p>先把知识变成行动，再用行动带来新的理解。</p><a class="btn primary" :href="href('/guide/idea-to-customer')">开始学习 →</a><small>开放知识持续完善中 · 社区与企业服务仍在规划</small></section>
  </main>
</template>
