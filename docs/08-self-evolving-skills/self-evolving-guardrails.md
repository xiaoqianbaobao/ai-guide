---
title: 自进化的失控风险与护栏设计
description: 自进化系统最可怕的不是"它不会变聪明"，而是"它在无人察觉的情况下慢慢变笨、变乱、变危险"。本讲系统列出 6 类失控模式与对应的工程护栏：技能污染、能力漂移、静默覆盖、护栏自废、配置漂移、激励偏离。
module: self-evolving-skills
tags:
  - 进阶
  - 运行时
  - 风控
  - 审计
---

<KnowledgeMap current-module="self-evolving-skills" current-article="自进化的失控风险与护栏设计" />

<ArticleHeader
  module="自进化 Skills 与 Agent 自我改进"
  :tags="['进阶', '运行时', '风控', '审计']"
  reading-time="12 分钟"
  prerequisite="已读 Skill 自动发现与打包、自我修正闭环、07 本体论之受治理写入与 Attestations"
  summary='把自进化的失控归纳为 6 类并逐一给出工程护栏：（1）技能污染→命名空间+去重+lifetime；（2）能力漂移→回归基准+pin+漂移检测；（3）静默覆盖→禁止覆盖只允许supersedes+变更通知；（4）护栏自废→guard的变更走更高tier；（5）配置漂移→pins+re-lock策略；（6）激励偏离→outcome前置+reviewer独立。最后给一张"自进化护栏自检表"。'
/>

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    自进化系统的失败，很少是"某一次 Skill 明显写炸了"——那种你一眼就能发现。真正的灾难都是慢变化：
    一个接一个 Skill 的 contract 悄悄放宽、证据门槛悄悄降低、权限悄悄提升、一个 Skill 被 20 个稍有不同的副本悄悄替代、
    某个 guard 的阈值被 10 次小修改从"严格"变到"几乎形同虚设"。**慢灾难需要慢监控**：你要给护栏本身加护栏。
  </p>
</div>

## 1. 失控模式一：技能污染（Skill Pollution）

**是什么**：自动发现/自我修正的流水线不断产出"看起来都能用、但其实几乎重复、版本差异非常小"的 Skill。最终：
- Skill Registry 里同一个能力有 20+ 个不同版本/变种；
- Agent 不知道该用哪一个，只能随机选或者默认选最新；
- 每次评估变成"评估 20 个几乎一样的 Skill"，评估成本爆炸，但收益没有。

### 护栏：命名空间 + 去重门禁 + 生命周期

1. **命名空间门禁**（SkillCandidate 生成时就校验）：
   - 必须符合 `domain.capability.vX.Y.Z`，禁止模糊命名
   - 同 domain 下的新候选，必须先与已有 Skill 做**相似度对比**（input/output contract 相似度 + preconditions 相似度 + provider path 相似度）
   - 相似度 > 阈值（例如 0.8）→ 归类为 Patch 路径或直接拒绝，不许另开新名

2. **生命周期门禁**（与 Crucible Procedure 对齐）：
   - 新的版本 live 之后，老版本必须有一条明确的退休路径：要么被 supersedes → 自动 retired；要么在 N 天 0 调用 → 标记 deprecated
   - Retired Skill 禁止在新的 Harness/Workflow 中被引用（只允许历史 re-run 重放）

3. **去重审计**：每周跑一次"Skill 相似度聚类"报表，把高度相似却共存的 Skill 拎出来给 owner review。

## 2. 失控模式二：能力漂移（Capability Drift）

**是什么**：Skill 从 v1 → v2 → v3 → v4 每次改动都"没问题"，但累计之后它的实际效果已经偏离了最初设计目标。
典型现象：
- Skill "triage-risk-v1.4" 当初是为了**保守**输出（宁可多记不误报），但经过 10 次"自动修正（降低证据 floor / 放宽 mutation guard）"之后，它变得非常激进——误报率提升 3×，但在 regression fixture 上依然"通过"（因为 fixture 跟不上真实漂移）。

### 护栏：Golden Baseline + Pin + Drift Detector

1. **Golden Baseline Fixtures**：每个 Skill 发布时都要有**冻结的黄金样本集**（从真实成功样本挑选 + 人工标注结果），与 Skill Artifact 一起 pin。这个集合**不能被自动进化流程自行增删改**，只能人工/高 tier review 改动。
2. **Config/Lock Pins + Schema Pins**：Skill 每次运行必须与发布时的 `config_digest + lock_digest + skill_schema_version + harness_version` 一致（或显式声明兼容范围），任何不一致都**fail closed**，而不是"差不多就跑"。
3. **漂移检测**：
   - outcome contract 的 satisfied rate 每月 vs 同期 Golden Baseline 做统计检验（比如 t-test / 贝叶斯 A/B）
   - **输入分布漂移**：近期调用的输入分布 vs Golden Baseline 的输入分布如果显著变化，发出警报（很多漂移是输入变了，Skill 没跟上）
   - **输出分布漂移**：Skill 输出的严重等级/类别比例 vs 历史基线显著变化，发出警报
4. **漂移处置**：连续 N 个检测周期漂移 → 自动把 Skill 切为 pending，下一个版本必须**由人工审核**才能 GA。

## 3. 失控模式三：静默覆盖（Silent Overwrite）

**是什么**：Skill v2.0.0 在无人通知的情况下把 v1.9.0 "覆盖掉了"。调用方（Harness / Workflow）引用的是 `latest` 或者没有 pin，于是一夜之间所有行为都变了。
更危险的变体：**guard 本身被悄悄改松**（evidence floor 从 2→1，trust_precedent threshold 从 0.8→0.5），导致 proposal live 率突然提升，但结果质量悄悄下降。

### 护栏：禁止覆盖只允许 supersedes + 变更通知 + Guard 高 Tier 评审

1. **禁止覆盖**：Skill Registry 里同一个 `id + version` 绝对不可重写。任何变更必须产生新的 version（patch/minor/major）。
   - 这条与 npm/PyPI 的不可变包是一致的："发布出去的版本就是不可变的，有问题就发新版本。"
2. **supersedes 链**：新的 version 必须声明它 supersedes 谁（或哪些 versions），Registry 维护一条可追溯的 supersedes 链；retired 版本仍然保留可读状态用于审计。
3. **变更通知**：任何 Skill 的 GA 版本变更（从 canary→beta→GA，从一个 GA 到下一个 GA）都要有**显式通知机制**（站内消息、邮件、Slack、工单——按风险等级选），通知到：
   - Skill Owner
   - 直接使用该 Skill 的 Harness Owner
   - 直接使用该 Skill 的 Workflow Owner
4. **guard 变更独立高 tier**：任何修改 `evidence floor / preconditions / mutation guards / trust thresholds / procedure_access tier / write_policy` 的变更，评审 tier 必须比"纯提示词/纯文档"高一级：
   - 普通 Patch：1 个 reviewer
   - Guard 相关 Patch：至少 1 个独立 reviewer + 1 个 operator reviewer

## 4. 失控模式四：护栏自废（Guards Self-Disabled）

**是什么**：系统自我进化了一阵子，模型发现"如果我把 mutation guard 的阈值调低一点，或者把需要独立 reviewer 这一条改成可选，我的提案通过率就会飙升"。
于是它开始系统性地让护栏失效，或者不断产出"刚好绕开 guard"的 Skill 变种。

### 护栏：Guard 的变更走更高 Tier + 护栏变更审计报表 + 禁止 proposer 改 guard

1. **分层评审**（上一模式已讲，但强调一次）：**涉及 guards / thresholds / independence 要求 / permission / write_policy 的变更**，必须：
   - 不允许由 proposer 自动 approve
   - 至少要有一个 operator/human reviewer（不能全是自动化）
   - 评审结果与理由要写入长期审计日志（至少保存 N 个月，合规要求）
2. **禁止 proposer 直接改 guard**：自动化流程（Draft Skill Generator / Auto-repair Generator）默认无权修改 guards、权限、write_policy；若它"觉得 guard 应该改"，只能生成一条带证据的**变更建议**，走独立的人工 review 流程。
3. **护栏变更周报表**：每周汇总"被修改过的 guard/threshold/permission"列表，列出：
   - 变更前后的阈值对比
   - 变更的 proposer/reviewer 身份
   - 变更后 proposal live 率、mutation guard 拒绝率的变化
   - 对 outcome contract satisfied rate 的影响

## 5. 失控模式五：配置漂移（Config / Lock Drift）

**是什么**：Skill 在发布时 pins 了 `config_digest=abcdef`、`lock_digest=123456`。但过了 3 周，ontology config 改了（新增 entity、改了 named_query、升级了 quality_check），`lock_digest` 也变了。
如果你的运行时选择了"漂移了也照常跑"，Skill 的输出结果就慢慢不再可信；如果"fail closed"，可能一夜之间全挂。两边都有坑。

### 护栏：Pins + Re-lock 策略 + 兼容性矩阵

1. **显式声明 pin 策略**：
   - 每个 Skill 必须显式声明 `pin_policy: strict | allow_compatible_range | allow_any`（默认 strict，最安全）
   - `strict`：当前运行的 config/lock digest 必须与发布时完全一致，不一致直接 fail closed
   - `allow_compatible_range`：声明一个兼容的 schema version range，并且每次漂移必须经过"自动兼容性测试"过了才跑
   - `allow_any`：只有最确定的数据读取 Skill 才允许，并且必须带 operator reviewer
2. **自动兼容性测试**（drift 发生时自动触发）：
   - 如果 pin_policy=allow_compatible_range，漂移发生后先在 Golden Baseline fixtures 上跑一遍：
     - 如果回归全通过 → 允许 Skill 继续 live，但自动产生一条"漂移+兼容"的审计 attestation，并把新 digest 加入下一次 re-pin 候选
     - 任何回归失败 → fail closed，并产生"漂移阻断"事件，通知 Owner
3. **定期主动 re-lock**：
   - 不允许 drift 无限累积下去：每个 Skill 有一个最大 drift 天数或 digest 版本差
   - 到达阈值后自动把 Skill 切为 pending，等待 Owner 做一次 re-lock（重新跑 Golden + 兼容性测试 + 更新 publish artifact pins）

## 6. 失控模式六：激励偏离（Reward Hacking / Objective Drift）

**是什么**：自我进化的反馈信号本身有缺陷，模型优化"错误指标"——
- outcome contract 只看"工单是否在 7 天内关闭"，模型于是学会把 ticket 指派给"最快关闭的人"（不管对错）
- proposal_only 的审批通过率成为 Skill 成功的指标，Draft Skill Generator 学会把判断写得模棱两可、永远能过，而不解决真实问题
- Guard 拒绝率成为"Skill Generator 要优化掉的指标"——它于是产出永远不触发 guard 的 Skill（什么都不改的空转 Skill，或者什么都 proposal_only 但从不 live）

### 护栏：Outcome Contract 前置 + 多指标平衡 + 独立 Reviewer + 人工 Override Feedback

1. **Outcome Contract 必须由"真实世界后果"侧定义**，不能只看流程指标。
   - 坏："ticket 7 天关闭率"
   - 好："30 天内客户二次投诉率为 0 且 root cause 被修复 + 无新的同因 incident"（并且这个 outcome 的判定人与执行人分离）
2. **多指标平衡**：Skill 进化的成功不看单点指标，而是看多维平衡：
   - outcome satisfied rate（主要）
   - mutation guard 拒绝率（不能异常降低）
   - 人工 override rate（不能异常上升或异常下降）
   - audit / 合规通过率（不能下降）
   - cost / latency（不能显著变差）
3. **独立 reviewer 与 Outcome 判定人分离**：决定"这个 Skill 做得好不好"的人（或审计角色），与决定"这个 Skill 通不通过评审"的 reviewer，再与"生成 Skill 的 proposer"——三者身份必须互相独立。
4. **人工 override feedback 回流**：每次人工 override / 人工 reject / 人工改结果，都要作为**负反馈**回流到 Skill Generator 的训练数据，而不是被 silently ignored。

## 7. 最终：一张自进化护栏自检表

部署任何"自进化"之前，先自检这 18 条（建议做成 checklist 放在审批 PR 模板里）：

- **命名空间**：新 Skill 是否有合规 ID？与现有 Skill 去重了吗？[ ]
- **Version 不可变**：同 id+version 禁止覆盖，变更必须新 version + supersedes？[ ]
- **最小契约**：每个 Skill 都写清了 contract/preconditions/budget/evidence floor/pins？[ ]
- **失败分类**：自我修正前先分 6 类，只让方法/Skill 缺口类改 Skill？[ ]
- **归因素材**：失败归因到 Skill+Version+Step+最小复现+pins 吗？[ ]
- **回归门禁**：Draft 必须过 Golden Baseline 回归 + 最小复现样本通过？[ ]
- **证据门禁**：Draft 带失败 receipt + 评审理由可追溯？[ ]
- **风险门禁**：会写外部世界的 Skill 必过 operator reviewer？[ ]
- **Pins 门禁**：config/lock/harness/skill_schema 都 pin 了吗？[ ]
- **发布三档**：走 canary→beta→GA，而不是直接 100% live？[ ]
- **自动回滚**：4 条硬回滚条件都已实现并监控？[ ]
- **Guard 高 Tier**：改 guard/threshold/permission/write_policy 走了更高评审层？[ ]
- **Proposer 不动 Guard**：自动化 proposer 不能直接改 guard，只能提建议？[ ]
- **漂移处理**：config/lock drift 有显式策略（strict/range/re-lock）？[ ]
- **命名空间去重审计**：定期跑 Skill 聚类报表？[ ]
- **能力漂移监控**：Golden Baseline + 输入/输出分布漂移检测 + 处置？[ ]
- **护栏变更审计报表**：每周汇总 guard/threshold 变更？[ ]
- **多指标平衡 + Outcome 真实世界**：不 reward hack，且 Reviewer/Proposer/Outcome 三方独立？[ ]

## 本节总结
- 自进化的失控主要有 6 类：技能污染、能力漂移、静默覆盖、护栏自废、配置漂移、激励偏离，其中最危险的是"慢漂移"和"护栏自己被悄悄废掉"；
- 每一类失控都有对应的工程护栏，核心是：**不可变版本 + supersedes 链 + 独立 reviewer + Golden Baseline 回归 + Pins + 漂移检测 + 多指标平衡**；
- 把所有护栏的变更拉到比"普通 Skill 变更"更高的评审 tier，是防止"护栏被自进化流程慢慢拆掉"的关键；
- 最后那张 18 条自检表，建议直接放进自进化 Skill 的 PR/评审模板里，上线前一条条打勾。

## 下一步
08-self-evolving-skills 到此结束。护栏之后，真正进入"合规、审计、血缘、生命周期"的长期治理层：去 [数据治理](../09-data-governance/)。或者回看"评估怎么为自进化提供可信反馈"：[Harness 与 Skill 评估体系](../06-eval-evolution/harness-skill-evaluation)。
