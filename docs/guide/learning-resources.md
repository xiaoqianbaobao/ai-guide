---
title: 系统学习资源：数学、模型、Agent 与产品
description: 精选课程、官方教程和书籍，为每一项资源给出学习目标
---

# 系统学习资源：数学、模型、Agent 与产品

这些资源按学习目标组织。站点外的课程和工具会更新，运行代码前检查版本与费用。资源推荐不代表我们逐章复现或完整阅读过所有资料；书籍可能需要购买或订阅。

## 数学与机器学习

| 资源 | 形式与适合对象 | 学完尝试 |
| --- | --- | --- |
| [3Blue1Brown：线性代数的本质，第一讲](https://www.youtube.com/watch?v=fNk_zzaMoSs) | 视频系列第一讲；适合建立向量的几何直觉 | 画出向量；继续学习后解释矩阵列与基向量的关系 |
| [Stanford CS229：机器学习第一讲](https://www.youtube.com/watch?v=Bl4Feh_Mjvo) | 斯坦福课程视频；需要数学和 Python 基础 | 区分监督学习、训练集和测试集，并解释过拟合 |
| [PyTorch：Deep Learning with PyTorch: A 60 Minute Blitz](https://docs.pytorch.org/tutorials/beginner/blitz/index.html) | 官方动手教程，包含张量、自动微分、神经网络与分类器 | 跑通分类示例，记录依赖、训练与验证结果，并改变一个参数比较 |
| [Stanford CS224W：图机器学习](https://cs224w.stanford.edu/) | 图机器学习课程材料；适合已有机器学习基础者 | 解释节点、边、消息传递，并在小图中手算一次聚合 |

视频适合直觉建立，不能取代动手：从课程中选一个例子，说明输入、输出、假设、失败条件并复现。尤其不要把某次训练结果当作模型在所有数据上的效果。

## Agent 工程与评估

- [Anthropic：长任务应用的 Harness 设计](https://www.anthropic.com/research/harness-design-long-running-apps)：研究跨会话交接、生成与评价的组织。配合本站 [Agent 工程闭环](../05-tools-frameworks/agent-engineering-loop)阅读，写出一次中断恢复所需的状态。
- [Anthropic：Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)：理解任务、轨迹、评分和环境的作用。结合 [线上评估与回归](../06-eval-evolution/production-evaluation-loop)设计一个可复现的失败样本。
- [OpenAI：Agent Improvement Loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)：查看轨迹和反馈如何转成回归评估。运行前核对依赖、外部服务与费用。

## 产品、用户与企业交付

- [YC：Building Product, Talking to Users, and Growing](https://www.ycombinator.com/library/dS-how-to-start-a-startup-building-product-talking-to-users-and-growing)：创始人讲座，含视频与文字记录。练习区分用户提出的功能和背后的问题；企业客户还需额外考虑采购、权限与组织约束。
- [YC Startup School：How to Get Your First 10 Customers](https://www.ycombinator.com/library/SF-how-to-get-your-first-10-customers)：视频及文字记录，讨论如何寻找首批目标客户和开始对话。看完后，为一个具体行业写下“目标角色在哪里开展工作、可能遇到什么问题、可以通过谁介绍”；再用本站[客户访谈实战](../10-product-fde/customer-discovery)中的问题卡验证，而不是把观看后的猜测当作客户需求。视频是创业者经验汇总，不保证任何渠道或转化率适用于你的行业。页面标题与文字记录核验于 2026-11-28；未逐段验证视频内容与字幕一致。
- [YC Startup School 视频目录](https://www.ycombinator.com/blog/startup-school-videos)：按访谈、定价、最小可行产品和融资挑选主题；不要把早期创业建议机械套用到大型企业交付。
- [Martin Fowler：Outcome Over Output](https://martinfowler.com/bliki/OutcomeOverOutput.html)：从交付物转向用户成效，并理解结果归因的困难；参见本站 [从功能交付到客户成效](../10-product-fde/outcome-over-output)。
- [《Inspired》，Marty Cagan，第二版](https://www.oreilly.com/library/view/inspired-2nd-edition/9781119387503/)：根据公开目录，适合进一步学习产品团队与产品发现。完整内容可能需要订阅；本站尚未提供逐章读书笔记。
- [Steve Blank：Customer Discovery 与相关书籍介绍](https://steveblank.com/2010/08/26/)：了解客户开发为什么先验证问题和商业假设；结合当前业务重新检验，勿照搬早期创业场景。
