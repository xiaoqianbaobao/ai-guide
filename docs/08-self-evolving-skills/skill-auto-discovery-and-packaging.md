---
title: Skill 的自动发现与自动打包机制
description: 自进化的第一步不是"让模型自己改代码"，而是把"哪些反复出现的成功动作可以被固化成一个 Skill"这件事做成可观察、可评审、可版本化的运行时产物。本讲讲发现→候选→评审→打包→发布的闭环。
module: self-evolving-skills
tags:
  - 进阶
  - 运行时
  - Skills
---

<KnowledgeMap current-module="self-evolving-skills" current-article="Skill 的自动发现与自动打包机制" />

<ArticleHeader
  module="自进化 Skills 与 Agent 自我改进"
  :tags="['进阶', '运行时', 'Skills']"
  reading-time="13 分钟"
  prerequisite="已读 05-tools-frameworks: Agent Skills、Harness 设计、06 评估体系、以及 07 本体论之 Cruxible YAML 本体与受治理写入"
  summary='把"自动进化 Skill"拆解成五步：（1）运行时日志里的信号发现；（2）生成候选 Skill 提案；（3）独立评审 + 门禁校验；（4）打包成符合 Harness 规范的版本化产物；（5）灰度发布与回滚。全程参考 Crucible Procedure 的 proposal-only/live/supersedes 生命周期与 config/lock pins，保证不是"模型偷偷改自己"，而是每一步都有 receipt。'
/>

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    一提到"自进化"，大家很容易想到"模型自己写代码并部署自己"。工程上更靠谱、也更可控的版本其实是：**模型自己只负责生成「把重复出现的成功模式抽象成 Skill 的候选提案」，剩下的评审、门禁、打包、发布全部走与代码合并一样严格的受控流程。** 发现阶段看日志，提案阶段走 review，打包阶段用 Harness/Skill schema，发布阶段有灰度、有 pin、有回滚——这才是"自进化"的工程版本。
  </p>
</div>

## 1. 先定义清楚：我们说的 Skill 到底是什么

05-tools-frameworks 的 [Agent Skills](../05-tools-frameworks/agent-skills) 与 [Harness 设计](../05-tools-frameworks/harness-design) 已经给出 Skill 的最低必要结构（你可以把它类比为 Cruxible Procedure 的上层可复用版本）：

```yaml
skill:
  id: triage-new-incident-from-kb
  version: "1.2.0"
  description: 从 KEV/NVD/内部资产快照三件套输出受影响供应商清单并创建治理工单
  tags: [incident, triage, proposal_only]
  input_schema:
    incident_id: string
    effective_from: datetime
    output_format: enum(json_markdown, crux_candidate_group)
  required_evidence:
    - source: kev_reference_snapshot
    - source: asset_snapshot
  preconditions:
    # 引用 Ontology named_query 的前置结果非空
    named_query("at_risk_asset_scope_without_vendor_controls"):
      min_count: 1
  budget:
    max_provider_calls: 18
    wall_clock_s: 540
  procedure_access: governed_write
  acceptance:
    requires_independent_reviewer: true
    pins: [config_digest, lock_digest]
    outcome_profile: triage_accuracy_by_sla_v3
```

"自进化"围绕的就是**这份 schema 的从 0 到 1、从 1 到 n 的受控生命周期**。

## 2. 发现（Discovery）：从运行时日志里抽取"值得被固化"的模式

不要一上来就要求"模型发现一切"。先定义 4 类"高价值发现信号"，任何一类命中都进入候选池：

### 2.1 重复度信号（成本/延迟角度）
- 同一组 Tool/MCP/Provider 调用链，在 14 天窗口内出现 ≥ N 次（比如 ≥ 5 次）
- 这些调用链的输入/输出形状在 **contract 层**上高度相似（字段相似度 / 结构对齐）
- 单次执行的平均 wall-clock 或 provider 调用量超过阈值

Cruxible provider execution traces 天然能做这件事——每个 provider 的 `ExecutionTrace` + `receipt_id` 已经进了 `state.db`。

### 2.2 成功率信号（价值角度）
- 某段链路被多次人工 retry/override 之后最终走通：说明当前 Skill 表达力不够，但"这个模式是有解的"
- 某段链路的 outcome contract 长期 satisfied：说明这个模式本身可靠，值得抽出来标准化

### 2.3 代码/笔记重复信号
- 多个 Agent（或同一个 Agent）在不同会话里反复写出几乎一样的 system prompt 片段 / tool 参数组合 / rubric
- 多个工程师 PR 里反复出现一样的 Harness patch / Skill wrapper（这个是人工发现的典型路径，依然要纳入）

### 2.4 合规/审计信号
- 某段链路频繁触发 review 的"总是被要求补充同一类证据"
- 某段链路长期 proposal_only，但 candidate group 的结构总是一模一样（说明可以固化为规范化 proposal 生成 Skill）

**发现阶段不写任何 Skill 文件、不改任何运行时配置。** 它只产出一个 `SkillDiscoveryRecord`：命中了哪些信号、使用了哪些 trace 样本、建议的 skill 命名空间与候选名称。

## 3. 候选（Proposal）：把发现物变成可评审 Skill Draft

一旦 DiscoveryRecord 达标（例如命中 ≥ 2 类信号、样本数 ≥ 3、人工或 heuristic 确认），就进入候选生成阶段：

```mermaid
flowchart LR
  D[DiscoveryRecord + Trace samples] --> G[Candidate Generator<br/>可以是模型 + 模板]
  G --> S[Draft Skill YAML<br/>符合 Harness schema]
  G --> T[Draft tests/fixtures<br/>从样本中抽]
  G --> E[Draft preconditions/evidence floor/budget]
  S + T + E --> P[SkillCandidate proposal]
  P --> CG[Candidate Group （proposal_only）]
```

候选阶段要**强制做 5 件事**，否则 proposal 直接被 mutation guard 拒绝：

1. **ID/命名空间**必须落入预定义的命名规范（`domain.name.vX.Y.Z`），防止 skill 名无节制膨胀；
2. **Input / Output Contract**必须显式写清，并与 Ontology（entity_types / contracts / named_queries）对齐；
3. **Budget** 必须声明：wall_clock_s、max_provider_calls、允许调用的 providers 白名单；
4. **Preconditions & Evidence floor**：必须写清它依赖哪些 named query 结果、哪些 source artifacts；
5. **Reviewer independence & Pins**：要求与该 skill 相关的运行时配置/lock 版本一起进入 Acceptance 条款（参考 Crucible procedure acceptance pins）。

生成 Draft Skill 的模型可以被视为 `proposer`——**它永远没有 graph_write 权限**，只能在 governed_write 下生成 candidate group proposal，永远不直接 live。

## 4. 评审（Review）：与代码 PR 同等严格

这一步是护栏的核心。不要让"自进化"变成"模型自己 approve 自己"。Crucible 对 Procedure 的要求我们升级到 Skill：

### 4.1 评审者身份分离
- SkillCandidate 的 proposer（生成 Draft 的模型/脚本/自动化流水线角色） **≠** 最终的 reviewer/approver
- 对"会触发任何外部写动作"的 Skill（例如会开 ticket、发消息、触发 pipeline）：必须额外过一个 operator-reviewer 角色（能看懂真实世界后果的人）

### 4.2 门禁检查（Guards，必须程序化）
在 resolve/approve 写卡口必须过：
- **结构门禁**：Draft Skill YAML 能通过 Harness/Skill schema validator（否则拒绝）
- **预算门禁**：budget ≤ 同类生产 Skill 的 P90（否则必须升级到更高 tier reviewer）
- **前置门禁**：preconditions 引用的 named query、evidence 要求确实存在于当前 ontology config
- **Provider 白名单**：Skill 只能调用 procedure_access 被导出的能力（和 Crucible Procedure 一样）
- **回归门禁**：至少跑一遍从 Discovery 样本里抽出来的 fixtures，结果与样本成功路径 contract 对齐（否则拒绝）
- **变更门禁**：如果这是一个 v2 替换 v1 的 supersedes 提案，必须说明变更原因、影响范围、回滚步骤

### 4.3 评审产物（receipted）
每个 approve/reject/withdraw 都写 receipt，记录：
- reviewer 身份、理由、时间
- 当时的 config_digest / lock_digest
- 跑过的 fixture run receipt ids
- 是否带超预算豁免/例外

这和代码 PR 的 Review + CI checks 是一一对应的，只是对象从代码变成 Skill Draft。

## 5. 打包（Packaging）：从 Draft 到可部署 Skill Artifact

一旦 Candidate Group 通过评审并 resolve=approved，打包阶段做 4 件事：

### 5.1 固化版本号
遵循 SemVer：
- **Patch**：文档、提示词小改、不改变 input/output contract
- **Minor**：新增可选参数、新增 capability（保持向后兼容）
- **Major**：input/output contract 变化、预算/门禁条款变化（不向后兼容）

> 这条可以直接照搬 Cruxible AGENTS.md 的版本约定，但把 prompt/config/contract 变化都升级为至少 minor。

### 5.2 绑定 digest pins
与 Crucible Procedure 的 pin 哲学一致：
```yaml
published_artifact:
  skill_id + version -> (
    accepted_against:
      config_digest, lock_digest, harness_version, skill_schema_version
    published_artifact_digest: sha256(...)
  )
```

### 5.3 生成可部署的 Skill Artifact
至少包含：
- `SKILL.md` 或 `skill.yaml`（schema）
- 参考 fixtures / golden 输入输出
- 回滚说明（影响范围、检测指标、如何 supersedes 到旧版本）
- 对应的 outcome profile 与预期达标阈值

### 5.4 登记到 Skill Registry
等价于你项目里的 Skills 索引表：谁发布的、何时发布、pin 到哪个 config/lock、超预算/超风险等级、当前生命周期状态（live / retired / pending / rejected）。

## 6. 发布（Release）：灰度 + 门控 + 回滚

Skill 发布和服务发布一样，必须可观测可回滚。推荐三档：

### 6.1 Canary（1%）
- 只对内部 sandbox/影子流量生效
- 要求 outcome contract 的命中率不低于上一版（或对照 baseline）
- 任何一次 mutation guard 拒绝或 outcome contract failed，自动拉响警报

### 6.2 Beta（10-30%）
- 扩展到一个小范围真实业务域
- 对 proposal 的 candidate group 产生的 live 判断保留审计抽样

### 6.3 GA（100% live）
- 要求连续 N 天 outcome satisfied_rate ≥ 阈值
- 保留灰度期间的全部 receipts 作为 live 的先例信任积累

发布时必须**禁止**的事情：
- 静默覆盖掉一个 live skill 定义（必须 supersedes 旧版本 + 旧版本转 retired）
- 发布后跳过 pins 校验（后续运行时 config/lock 漂移必须 fail closed）
- 没有回滚预案就发布

## 7. 一个完整的生命周期状态机

和 Crucible Procedure 对齐，Skill 的生命周期建议就是 6 态：

```text
discovered → candidate(pending_review)
  pending_review → live（独立评审通过，pin 成功）
  pending_review → rejected（评审拒绝，保留理由）
  pending_review → withdrawn（提案方主动撤回，无需 reviewer）
  live → retired（被新版本 supersedes，或主动下线）
  retired → 不可返回到 live，必须重新 propose replacement
```

每个状态转移都必须 receipted，并且 reviewer identity 必须满足 independence。

## 本节总结
- "Skill 自动发现与打包"不是模型偷偷改代码，而是**发现→候选→评审→打包→发布**的受控流水线；
- 发现靠 4 类运行时信号，不要依赖模型拍脑袋；
- 候选阶段强制写 contract/budget/preconditions/pins/evidence floor 五项最小契约；
- 评审阶段 reviewer 独立 + 程序化门禁（结构/预算/回归/provider白名单/变更），与 PR CI 等价；
- 打包阶段必须 SemVer + config/lock pins + 可部署 Artifact；
- 发布阶段灰度+门控+回滚三档，版本覆盖必须走 supersedes 而不是静默改写。

## 下一步
下一篇进入闭环的另一半：当运行时执行失败了，系统如何自我修正与自我生成新 Skill，见 [从执行失败到自我修正：生成新 Skill 的闭环](./self-improving-loop)。
