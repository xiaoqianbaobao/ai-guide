# AI Agent Guide - 选题看板与路线图

> 文档版本：v2.0 | 基准：[ai-agent-guide-spec-v2.md](./ai-agent-guide-spec-v2.md)
>
> 本看板把 "52 篇目标" 从一句话变成可追踪的任务列表。每篇状态：`📝 待写 / 🚧 草稿中 / ✅ 已发布 / ⚠️ 待复核`。

---

## 总体进度

| 模块 | 目标篇数 | 已发布 | 待写 | 完成度 |
|---|---|---|---|---|
| 00-preface 序章 | 4 | 4 | 0 | ✅ 100% |
| 01-llm-foundations 语言模型基础 | 14 | 14 | 0 | ✅ 100% |
| 02-agent-core Agent 核心机制 | 4 | 4 | 0 | ✅ 100% |
| 03-memory Memory 体系 | 5 | 2 | 3 | 🟡 40% |
| 04-multi-agent 多 Agent 系统 | 5 | 2 | 3 | 🟡 40% |
| 05-tools-frameworks 工具与框架 | 12 | 12 | 0 | ✅ 100% |
| 06-eval-evolution 评估与进化 | 5 | 4 | 1 | 🟡 80% |
| 07-ontology 本体论与知识表示 | 4 | 0 | 4 | 🔴 0% |
| 08-self-evolving-skills 自进化 Skills | 3 | 0 | 3 | 🔴 0% |
| 09-data-governance 数据治理 | 3 | 0 | 3 | 🔴 0% |
| **合计** | **59** | **42** | **17** | **🟡 71%** |

---

## 阶段一（0-4 周，短期高优先级）

### 03-memory 缺口（P0）

| 文章 | 状态 | 备注 |
|---|---|---|
| 记忆的写入时机与遗忘策略 | 📝 待写 | `four-memory-types.md` 结尾已有伏笔，可直接展开 |
| 向量库与图存储的选型对比 | 📝 待写 | 从"能存"到"该存在哪"的工程决策 |
| 从 Episodic 到 Semantic 的蒸馏流程实战 | 📝 待写 | 偏实战的记忆压缩 pipeline |

### 04-multi-agent 缺口（P0）

| 文章 | 状态 | 备注 |
|---|---|---|
| 多 Agent 的失败模式与恢复策略 | 📝 待写 | `orchestrator-subagent.md` 结尾已有"失败一/二/三"伏笔 |
| 多 Agent 的成本与延迟权衡 | 📝 待写 | Token 消耗随角色数量增长的工程账 |
| Blackboard / Debate 等非层级协作拓扑 | 📝 待写 | 目前只有 Orchestrator-Subagent 一种拓扑，缺对比 |

### 组件激活（P0，成本最低见效最快）

- [ ] 把 `Quiz` 组件接入现有 02-agent-core 和 05-tools-frameworks 的每篇结尾（1-2 题）
- [ ] 把 `ResourceCard` 组件用于"延伸阅读"卡片展示

### 工程治理（P1）

- [x] 建立本 `ROADMAP.md` 选题看板
- [ ] 每篇文章 frontmatter 增加 `last-verified` 字段（时效性复核）
- [ ] 发布前自查 checklist 文档化（ArticleHeader / 架构图 / 代码示例 / Quiz / KnowledgeMap）
- [x] 处理游离目录 `docs/agent/`（接入 guide 导航）

---

## 阶段二（5-12 周，新增模块骨架）

### 07-ontology 本体论与知识表示（P1）

| 文章 | 状态 | 备注 |
|---|---|---|
| Agent 系统里"本体"到底解决什么问题 | 📝 待写 | 实体消歧、关系建模、跨系统语义对齐 |
| Ontology vs Taxonomy vs Knowledge Graph 的边界 | 📝 待写 | - |
| Hypergraph 在企业级多 Agent 架构中的实际应用 | 📝 待写 | - |
| Schema 设计如何影响 Agent 的推理稳定性 | 📝 待写 | 回链 03-memory 和 04-multi-agent |

### 08-self-evolving-skills 自进化 Skills（P1）

| 文章 | 状态 | 备注 |
|---|---|---|
| Skill 的自动发现与自动打包机制 | 📝 待写 | 区别于 05 中的"人工设计 Skills" |
| 自我修正循环：从执行失败到生成新 Skill 的闭环 | 📝 待写 | - |
| 自进化机制的失控风险与护栏设计 | 📝 待写 | 技能污染、能力漂移、版本回滚，结合金融强监管背景 |

### 09-data-governance 数据治理（P1）

| 文章 | 状态 | 备注 |
|---|---|---|
| Agent 训练/记忆/RAG 语料的数据血缘 | 📝 待写 | 决策可追溯 |
| 敏感数据在 Memory 和 Tool 调用链路里的隔离设计 | 📝 待写 | - |
| 强监管场景的 Agent pipeline 合规落地 | 📝 待写 | 数据留存周期、审计日志、PII 脱敏，结合支付清结算背景 |

---

## 阶段三（持续迭代）

### 06-eval-evolution 扩容

| 文章 | 状态 | 备注 |
|---|---|---|
| 线上持续监控与劣化检测 | 📝 待写 | 区别于离线 benchmark |
| 评估体系本身的版本管理 | 📝 待写 | 评估标准也会过时，如何迭代 |

### 时效性复核机制

- 每季度抽查一次 `last-verified` 超过 6 个月的文章
- 尤其关注：框架选型、协议版本、API 用法、依赖兼容性

---

## 前端交互优化（按优先级排序）

### 优先级 1：激活已有组件
- [ ] Quiz 组件接入所有正文（每篇 1-2 道）
- [ ] ResourceCard 替换纯文字延伸阅读链接

### 优先级 2：进度可视化
- [ ] KnowledgeMap 增加已读/未读染色（基于 localStorage）
- [ ] 模块 index 页表格增加"已读"勾选

### 优先级 3：专注模式进阶
- [ ] 长文章渐进式折叠小节
- [ ] 代码块 & Mermaid 图点击放大

### 优先级 4：视觉细节
- [ ] 独立定义强调色（已读状态 / Quiz 正确反馈）
- [ ] 深色模式对比度实测

---

*本路线图随实际产出持续更新，每完成一篇请同步更新"已发布"列和对应文章的 `last-verified` frontmatter。*
