---
title: 从想法到第一个真实客户：实践路线
description: 用一个企业知识与工单助手案例，贯穿客户发现、产品构建、试点和价值验证。
---

# 从想法到第一个真实客户：实践路线

这条路线把 Builder（创造与交付）和 Seller（发现需求、建立信任、连接客户）放在同一个项目里练习。AI 是工具，Agent 是我们的第一个教学场景；识别问题、验证价值、交付结果的方法也可以迁移到其他行业。

我们使用一个贯穿案例：假设一家服务团队经常在多个文档中查找处理流程，员工需要重复询问资深同事。你想帮助团队更快找到可靠答案，并在需要时准备工单草稿。**这是虚构教学案例，不是已经完成的客户项目。**

## 第一阶段：发现问题

不要先问“你想不想要一个 AI 助手”，而要观察上一次工作是怎么发生的：谁遇到问题、找过哪里、花了多久、错误造成什么影响。访谈使用者，也访谈负责人；二者的目标可能不同。

**交付物：** 一张问题证据卡，写清用户、场景、现有办法、原始证据和仍待核实的假设。跟着 [客户访谈实战](../10-product-fde/customer-discovery) 完成第一版。

## 第二阶段：验证需求

挑选一个经常发生、代价可观察、拥有明确责任人的场景；记录哪些证据会推翻它。例如，若流程本身变化极少且用户已有准确入口，增加 Agent 可能只增加复杂度。明确用户、使用负责人和采购决策者分别是谁。

**交付物：** 一页试点假设：目标任务、使用对象、现有基线、风险、是否值得继续的条件。[从功能到客户成效](../10-product-fde/outcome-over-output) 可以帮助你把功能转换成结果指标。

## 第三阶段：做出产品

先做有边界的最小系统：用模拟文档回答问题并提供来源，资料不足时明确说不知道。把身份、授权、审批和故障恢复作为逐步完善的能力；不要因为演示成功就声称已经适合生产。

**交付物：** 可运行的最小原型、数据与权限边界、测试任务集。先运行 [只读知识助手教学原型](../agent/cases/knowledge-assistant-first-slice)，再体验[本地企业助手闭环](../agent/cases/enterprise-agent-local-lab)中的查询、审核与模拟工单。[企业级 Agent 实战路线](../agent/cases/enterprise-agent-roadmap)列出后续阶段的验收，整套生产级课程仍待完成。按需补充 [Agent 工程闭环](../05-tools-frameworks/agent-engineering-loop) 与 [线上评估](../06-eval-evolution/production-evaluation-loop)。

## 第四阶段：真实使用

和愿意参与的团队约定小范围、可撤回的试点：找出若干真实任务，在有权限的人监督下运行，记录人工处理时间、采用率、错误与纠正成本。先使用脱敏数据或明确获得授权的数据。

**交付物：** 试点方案、结果记录、用户反馈及下一次调整。真实使用者、试点客户和付费客户是不同阶段；有人试用并不等于有人付费。

## 第五阶段：争取成交

从客户确认过的收益与成本出发，讨论谁会采购、预算从哪里来、部署与支持如何收费。先说清边界、成功标准和结束条件，再提出报价。阅读 [从试点到第一个客户](../10-product-fde/pilot-to-first-customer)。

**交付物：** 一页价值说明、试点复盘和一份可讨论的合作提案。实际成交取决于客户、行业和执行，不由教程保证。

## 从哪里补课

- 技术背景：从 [AI 知识体系](./index) 出发，按需补模型、上下文、Agent 和工程。
- 产品与商业背景：先做 [客户访谈](../10-product-fde/customer-discovery)，再选择能解决问题的技术。
- 企业团队：先看 [企业实战路线](../agent/cases/enterprise-agent-roadmap) 中的治理与验收边界。团队课程、付费社区与个人服务还在规划。

这条路线是循环而非直线：新证据可能让你回到前一阶段，甚至决定不做。每次回退，都应该留下改变判断的证据。

## 配合学习：视频、课程与动手任务

下面选的是原作者或课程方提供的材料。视频以英文为主，平台的字幕、访问方式和课程收费可能变化；先完成对应练习，再把内容带回自己的场景。

| 阶段 | 推荐材料 | 看完后动手做什么 |
| --- | --- | --- |
| 发现问题 | [YC：How to Talk to Users](https://www.youtube.com/watch?v=MT4Ig2uqjTc)（视频） | 把三个“你会不会用”的问题改成“上次你怎么做”，用[问题证据卡](../10-product-fde/customer-discovery)记录观察与推断。 |
| 缩小产品范围 | [YC：How to Plan an MVP](https://www.ycombinator.com/library/6f-how-to-plan-an-mvp)（视频与文字） | 写下目标用户、一个具体任务和最小交付；再列出涉及安全和授权时不能省略的边界。 |
| 构建 Agent 基础 | [Hugging Face Agents Course：Unit 1](https://huggingface.co/learn/agents-course/en/unit1/introduction)（课程） | 画出一次工具调用的输入、动作和观察，再对照[只读原型](../agent/cases/knowledge-assistant-first-slice)说明哪些地方还没有引入模型。 |
| 检查系统质量 | [DeepLearning.AI：Building Systems with the ChatGPT API](https://www.deeplearning.ai/courses/chatgpt-building-system)（分节视频与代码） | 重点看评估相关课程，对照[本地回归示例](../agent/cases/knowledge-assistant-evaluation)写一条资料不足或越权用例；课程代码与 API 版本可能更新。 |
| 连接真实用户 | [YC：Building Product, Talking to Users, and Growing](https://www.ycombinator.com/library/dS-how-to-start-a-startup-building-product-talking-to-users-and-growing)（创始人演讲与文字） | 区分用户描述的问题与提出的功能方案，选择一条证据制定试点，而不是把每个建议都加进产品。 |

这些材料适用于学习思路，不保证适合每个行业。特别是企业场景，快速试错也应以授权、数据边界与可撤回性为前提。资源核验日期：2026-11-25。
