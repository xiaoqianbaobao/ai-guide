---
title: 从执行失败到自我修正：生成新 Skill 的闭环
description: 当 Agent 执行某 Skill 失败时，系统不应只把错误抛给用户。本讲把失败归因→定位缺口→生成候选修复/新 Skill→评审验证→发布，做成一条与代码 CI/CD 等价的「运行时自我进化闭环」，并把护栏嵌入每一步。
module: self-evolving-skills
tags:
  - 进阶
  - 运行时
  - 自我修正
---

<KnowledgeMap current-module="self-evolving-skills" current-article="从执行失败到自我修正：生成新 Skill 的闭环" />

<ArticleHeader
  module="自进化 Skills 与 Agent 自我改进"
  :tags="['进阶', '运行时', '自我修正']"
  reading-time="15 分钟"
  prerequisite="已读 Skill 自动发现与打包、06 评估与进化、07 本体论之受治理写入与 Evidence/Outcome"
  summary='把"自我修正"拆成 5 步：（1）失败分类器：把失败分到"数据缺、方法缺、Skill 缺、预算缺、配置错、权限错"6 类；（2）归因：定位到 Skill/Provider/Named Query/Permission 的精确责任点；（3）生成候选修复（改现有 Skill or 产生新 Skill Draft）；（4）评审与门禁（证据、独立 reviewer、回归 fixture、pins）；（5）发布（灰度+回滚）。每一步的失败再回流到下一轮训练样本，形成二次学习。全程参考 Cruxible feedback → outcome → receipts → proposal 循环，保证可审计。'
/>

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    不做分类的「自动重试」和「遇到错误就让模型自己重写提示词」不是自我进化，而是噪音放大器。真正靠谱的闭环第一步是先**把失败分类**：到底是数据没取到、还是 Skill 表达不了、还是证据不够、还是 budget 不够、还是权限不够？不同类失败对应完全不同的修复路径，只有"Skill 缺/方法缺"才走到"自动生成新 Skill"。其余类失败应该走：补数据/补权限/调预算/补 evidence——而不是让模型乱改 Skill。
  </p>
</div>

## 1. 先做一个失败分类器（这一步错了后面全错）

把所有运行时失败分成 6 类，分类**必须 receipted**（记录分类结果、当时执行快照、失败类型判断依据）：

| 失败类型 | 典型现象 | 是否需要改 Skill | 正确修复方向 |
| --- | --- | --- | --- |
| 数据缺口 | named query 结果空、snapshot 没取到、source artifact 缺失 | 否（除非 Skill preconditions 写松了） | 补数据/接入新的数据源/修 snapshot 逻辑 |
| 方法缺口 | 现有 Skill 流程能跑到某个点，但"这个问题根本没有被建模" | 是（需要新 Skill 或新 procedure） | 生成新 Skill（新的 procedure/named query 组合） |
| Skill 表达缺口 | 现有 Skill 逻辑有分支遗漏、contract 太严格、提示词/参数错 | 是（迭代现有 Skill，出 patch/minor 版本） | 改现有 Skill（补丁版） |
| 预算缺口 | provider 调用数/时间超 budget，不是不会做 | 否（除非是 Skill 设计太铺张） | 调 budget 上限或优化路径 |
| 权限缺口 | CRUXIBLE_MODE 下某工具被拒、reviewer 缺、procedure_access 不足 | 否 | 调 permission tier / 走审批 / 切换 proposal_only |
| 配置漂移 | config/lock digests 与 Skill pin 不一致 | 否 | re-lock 或升级 Skill pins |

**经验法则：只有「方法缺口 / Skill 表达缺口」才进入"自动改 Skill"路径；其余 4 类不要让模型碰 Skill 定义，而是走运维侧修复。**

## 2. 归因：定位到精确的责任点

分类之后第二步是"精确归因"——不能只说"失败了"，要定位到：

- 是哪一个 Skill / 哪一个 Harness / 哪一个 Procedure（精确到 `id+version`）？
- 失败发生在 Skill 的哪一步（步骤 ID、input/output artifact hash、receipt id）？
- 触发失败的**最小复现输入集**是什么（fixture 候选）？
- 当时的 pins：`config_digest / lock_digest / skill_schema_version / harness_version`？

Cruxible 的 receipts 天然支持这一步：每个 workflow/query/mutation/feedback 都有 receipt_id；provider 调用有 `ExecutionTrace`；outcome record 能把"用户说成功/失败"和"执行时的状态"接起来。把这些结构化日志聚合成一个 **Failure Attestation**——注意是 attestation，不是直接覆盖状态。

## 3. 候选修复：两种路径，两类 Draft

根据归因结果产出两类候选修复：

### 路径 A：Patch 现有 Skill（Skill 表达缺口）
典型触发：
- 某个 if 分支没覆盖到新的实体类型
- 某个 mutation guard 阈值太严，明明有足够证据但一直拒
- preconditions / evidence floor 写松了，导致后续步骤失败（或者反过来太严导致 preconditions 空）

产物：
- Draft Skill（同一 id，版本 bump：patch 或 minor）
- Diff：旧 vs 新 contract、旧 vs 新 budget、旧 vs 新 guard thresholds
- Fixtures：来自最小复现输入 + 对应期望结果（从"本该成功但失败"的历史结果抽）

### 路径 B：产生新 Skill（方法缺口）
典型触发：
- 现有所有 Skill 没有一个能处理该实体类型组合 / 业务域 / 新的审批模式
- 从失败日志里发现需要引入一组全新的 named query + workflow 组合
- 多 Agent Debates 里反复出现"某个问题没人真的能回答"

产物：
- 全新 Draft Skill（新 id，v0.1.0）
- 所依赖的 Ontology 变更提案（新增 entity_type / relationship / named_query / quality_check / matching rule —— 这部分**先进入本体 proposal_only 评审**，再把 Skill 评审依赖它）
- Fixtures：至少一个"能跑通新方法"的合成/真实样本

### 路径 C（禁止直接做，但要有）：运行时临时 fallback
对于"修不了、但不能阻塞用户"的场景，定义一个**临时 fallback**：
- 不写 Skill，不永久改变状态（最多写 feedback / attestation）
- 记录：fallback 触发次数、人工 override rate、outcome
- 这类 fallback 反哺"方法缺口"发现

## 4. 评审与门禁（Self-correction 护栏的命门）

候选修复和 Discovery 阶段的 SkillCandidate 走**同一套评审流水线**，但要额外加 4 条门禁：

### 4.1 回归门禁：必须在最小复现集上"现在能过、旧方法不过"
- Draft 修复必须在**最小复现 fixture** 上通过（修复了问题）
- 同时在"历史上成功的样本集合"上不能 regress（成功率不低于原 Skill baseline）
- 两条任何一条不过：自动 reject

### 4.2 风险门禁：对写操作的修复要更严
- 如果修复的 Skill 是 direct 写（graph_write / admin），必须给出理由为什么不能降级为 proposal_only
- 如果引入了新的 provider / 新的写目标 / 新的 permission 要求：必须升级评审 tier（operator reviewer 加入）

### 4.3 证据门禁：修复依据必须可追溯
- Draft 必须引用：失败 receipt id、归因结果、最小复现 fixture id、历史成功/失败 outcome
- **不能只靠模型认为"这版更合理"**——必须有可追溯的运行时证据支撑变更

### 4.4 Pins 门禁：config/lock 一致性
- 新 Skill 或新版本必须在**当前生效的 config_digest / lock_digest**下过验收
- 如果修复依赖了 ontology 的变更（新增 entity/query/quality_check），必须引用那些变更的 proposal receipt 与 approval receipt，不能"假设它们已经 live 了"

> 这 4 条 + 前一篇 Discovery→Review 的一般门禁，合起来就是"自我修正不会把系统改炸"的底裤。少任何一条都建议别开自动进化。

## 5. 发布：灰度 + 自动回滚触发

候选通过评审、打包成 Artifact 之后，发布不是 "100% live" 一步到位：

**三档发布（与 Discovery 发布路径一致，但回滚阈值更严格）：**
- **Canary（影子）**：与旧 Skill 并行跑，不写状态，比较两个版本的 outcome satisfied rate 是否显著提升
- **Beta（真实流量）**：写入 proposal_only 级状态，live 写入被关闭；一旦 mutation guard 拒绝率 > 基线 X%，自动回滚
- **GA（真实 live）**：只有 Beta 连续 N 次 outcome contract 达标后升级 GA

**自动回滚的硬条件（任何一条触发立即滚回）：**
1. GA 后 outcome satisfied rate 低于上一版 -Δpct（例如 -10%）
2. 任何一次 mutation guard 拒绝且拒绝原因是"新 Skill 引入的 contract 破坏"
3. 权限/Permission Denial 错误相比旧版显著上升
4. 人工 override rate 显著高于 baseline

回滚本身也是 receipted：谁回滚的、触发原因、当时的指标快照、涉及的 skill 版本。

## 6. 二次学习：把闭环变成"越修越聪明"

以上所有过程的结构化产物就是二次学习的黄金数据：

- **失败分类 + 归因 + 分类正确与否的反馈**：用于训练下一轮的失败分类器（减少"把数据缺口误判为 Skill 缺口"的假阳性）
- **候选修复通过/被拒的评审理由**：用于训练 Draft Skill 生成（减少评审被拒率）
- **回滚事件**：用于收紧自动发布的门禁（例如自动提升某类 Skill 的评审 tier）

这层二次学习不直接写 Skill，只产出运行时的 classifier 与 generator 新版本，本身也要走 proposal_only review——避免"学习器把自己学偏"。

## 本节总结
- 自我修正闭环的第一步是**失败分类**，6 类里只有"方法缺口 / Skill 表达缺口"才该去改 Skill；
- 归因要精确到 Skill+Version+Step+最小复现输入+pins，靠 receipts 和 provider execution trace；
- 修复分"Patch 旧 Skill / 产新 Skill / 临时 fallback"三条路径，不能混成一条；
- 评审额外过 4 条门禁：回归 / 风险 / 证据 / Pins；
- 发布三档 + 4 条硬回滚条件，回滚本身也要 receipted；
- 全过程的结构化产物回流，训练下一轮分类器与生成器，形成真正的越用越强。

## 下一步
当这套自我修正真的跑起来时，新的风险也随之出现：能力漂移、技能污染、静默覆盖、运行时自升级无人发现。下一篇读 [自进化的失控风险与护栏设计](./self-evolving-guardrails)。
