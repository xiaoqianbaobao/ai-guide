---
title: Orchestrator-Subagent
description: 用协调者与执行者分工处理复杂任务
module: multi-agent
tags:
  - 核心
---

<KnowledgeMap current-module="multi-agent" current-article="Orchestrator-Subagent" />

# Orchestrator-Subagent：指挥者与执行者

<ArticleHeader
  module="多 Agent 系统"
  :tags="['核心']"
  reading-time="11 分钟"
  prerequisite="理解 Agent 基本闭环"
  summary="多 Agent 系统最常见的结构，不是所有 Agent 平等协作，而是由一个 Orchestrator 负责任务分解和结果聚合，再让多个 Subagent 专注执行各自的局部任务。"
/>

## 为什么要这样分工

复杂任务往往同时包含全局目标管理、局部任务执行和结果聚合与回滚。把这些职责都塞进一个 Agent，通常既浪费上下文，又会让推理过程越来越混乱。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    多 Agent 的价值不在于多几个模型一起跑，而在于通过角色分工，把全局协调和局部执行拆开处理。
  </p>
</div>

## 先区分一个误解

很多人一提到多 Agent，第一反应是：

- 多开几个模型并行跑
- 给每个 Agent 起个不同名字
- 让它们互相对话几轮

这些都不等于真正的多 Agent 系统。

一个更有价值的多 Agent 结构，应该先回答三个问题：

- 谁负责理解总目标
- 谁负责执行局部任务
- 谁负责合并结果并决定下一步

`Orchestrator-Subagent` 正是在解决这三个问题。

## 这个结构的最小定义

在这种模式里，系统通常至少包含两类角色：

- `Orchestrator`
  - 负责理解用户总目标
  - 把任务拆成若干可执行子任务
  - 决定调用哪个 Subagent
  - 汇总结果并判断是否继续
- `Subagent`
  - 负责完成某个局部任务
  - 只关注自己当前职责
  - 把结果回传给 Orchestrator

可以把它理解成：

```text
用户目标
  -> Orchestrator 负责拆解与调度
    -> Subagent A 执行任务
    -> Subagent B 执行任务
    -> Subagent C 执行任务
  -> Orchestrator 汇总结果并输出
```

## 为什么单 Agent 在复杂任务里会吃力

假设你要完成这样一个任务：

> 分析一个 GitHub 仓库，找出部署失败原因，修改配置文件，然后总结变更并更新文档。

如果让单个 Agent 一口气做完，它需要同时处理：

- 对总任务的理解
- 对代码仓库结构的搜索
- 对配置错误的定位
- 对修改方案的判断
- 对结果验证和总结的组织

这些角色混在同一个上下文里，会出现几个典型问题：

- 上下文越来越长，重点越来越模糊
- 局部细节容易污染全局判断
- 任务切换频繁，推理成本变高
- 失败后难以定位到底是哪个环节出错

而在 `Orchestrator-Subagent` 结构里，可以拆成：

- Orchestrator：负责总流程
- Search Subagent：负责找问题位置
- Editor Subagent：负责修改文件
- Validator Subagent：负责构建和检查

这样每个角色的上下文都会更短、更稳定，也更容易评估和复用。

## 什么时候应该考虑这种结构

下面这些场景，通常比单 Agent 更适合采用 Orchestrator-Subagent：

- 任务天然可以拆成多个阶段
- 各阶段需要不同工具集或权限
- 某些子任务可以并行处理
- 你希望记录和评估每个子任务的行为
- 单 Agent 的上下文已经开始失控

反过来说，如果任务很短、目标很清晰、步骤也不多，就不一定要上多 Agent。

多 Agent 的前提不是“听起来更高级”，而是：

`拆分之后，系统整体会更清晰、更可控`

## 这种结构最核心的收益

### 收益一：把全局管理和局部执行拆开

Orchestrator 关注的是：

- 目标是什么
- 当前进度到哪里
- 还有哪些子任务没完成
- 最终输出要怎么收束

Subagent 关注的是：

- 这个局部任务具体怎么做
- 需要什么工具
- 当前结果是否完成

这种分工可以显著减少角色混杂带来的推理噪声。

### 收益二：更容易做权限和工具隔离

不同 Subagent 可以拥有不同的能力边界。例如：

- 搜索型 Agent 只有读取和搜索能力
- 编辑型 Agent 才有修改文件权限
- 测试型 Agent 只负责执行验证命令

这不仅让系统更清晰，也更安全。

### 收益三：更方便评估和替换

当系统拆成多个子角色之后，你可以单独观察：

- 哪个子任务经常失败
- 哪个角色的输出质量差
- 哪个阶段最耗时

这样后续优化就不再是“整个系统看起来不太行”，而是能定位到更具体的环节。

## 最常见的失败模式

### 失败一：拆得太细

如果任何一步都单独拆成一个 Agent，会带来：

- 调度成本过高
- 状态传递复杂
- 结果整合困难

拆分不是越细越好，而是要围绕“职责边界”来拆，而不是围绕“每个动作”来拆。

### 失败二：Orchestrator 变成新的单点瓶颈

如果所有判断都堆给 Orchestrator，它会重新变成一个“超大单 Agent”。

这时虽然形式上有多个 Agent，但本质上只是把几个执行器挂在一个过载的大脑后面。

### 失败三：Subagent 缺乏清晰输入输出

如果 Subagent 接到的任务描述太模糊，就会出现：

- 角色职责漂移
- 输出格式不一致
- Orchestrator 无法稳定汇总结果

所以多 Agent 设计里，一个非常关键的工作是：

`为每个 Subagent 定义清楚的输入、输出和完成标准`

## 一个简化示例

下面是一个很简化的伪代码：

```python
def orchestrate(user_task):
    plan = break_down(user_task)

    results = []
    for step in plan:
        agent = pick_subagent(step)
        result = agent.run(step)
        results.append(result)

        if not result["success"]:
            return recover_or_retry(step, result)

    return summarize(results)
```

这里最关键的不是代码写法，而是背后的结构含义：

- `break_down()` 负责拆分任务
- `pick_subagent()` 负责路由
- 每个子角色只处理自己的局部任务
- 最终由 Orchestrator 做汇总和恢复判断

## 和工作流系统有什么区别

这也是一个非常容易混淆的问题。

如果一条流程完全由固定规则决定，比如：

```text
先读文件 -> 再调用接口 -> 然后发邮件
```

这更接近工作流。

而 Orchestrator-Subagent 更适合下面这种情况：

- 任务拆分方式不是固定的
- 要根据当前上下文决定调谁
- 某些子步骤需要动态重试或改写
- 最终收束方式也可能变化

所以它不是静态编排，而是：

`由一个协调角色动态决定如何编排多个执行角色`

## 设计时最值得关注的 4 个点

- `拆分边界`
  - 按职责拆，而不是按动作数量拆
- `上下文隔离`
  - 不同 Subagent 不要共享过多无关上下文
- `输出格式`
  - 每个子角色都要有可汇总的稳定输出
- `失败恢复`
  - Orchestrator 要能判断重试、改写还是终止

## 再区分一个容易混淆的概念：Harness

当你开始做多 Agent 系统时，很多人会把“调度结构”和“运行外壳”混在一起。

但它们其实解决的是不同问题：

- `Orchestrator-Subagent` 解决的是角色如何分工
- `Harness` 解决的是整套系统如何跨多轮、多窗口持续运行

也就是说：

- Orchestrator 决定“谁去做”
- Harness 决定“这一整套协作如何稳定做下去”

如果没有 harness，多 Agent 系统也可能在长任务里出现：

- 回合切换后失去进展
- 中间状态交接不清
- 某个 Subagent 做完后没人留下结构化结果

所以一旦系统进入长任务阶段，多 Agent 拓扑和 harness 往往需要一起设计。

## 本节总结

- 多 Agent 的价值在于角色分工，而不是模型数量
- Orchestrator 负责全局目标、调度和结果汇总
- Subagent 负责局部任务执行和结果回传
- 这种结构适合复杂、多阶段、可拆分的任务
- 设计重点在职责边界、上下文隔离和失败恢复

## 下一步

如果你已经理解了多 Agent 的基本协作拓扑，下一步建议阅读 [MCP 协议](./mcp-protocol)，看标准化工具接入为什么会成为多 Agent 和 AI 工具系统的基础设施。
