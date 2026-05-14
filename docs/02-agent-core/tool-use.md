---
title: Tool Use 完整机制
description: 拆解模型如何发起工具调用、宿主如何执行，以及结果如何回注
module: agent
tags:
  - 核心
---

<KnowledgeMap current-module="agent" current-article="Tool Use 完整机制" />

# Tool Use：让模型从会说到会做

<ArticleHeader
  module="Agent 核心机制"
  :tags="['核心']"
  reading-time="14 分钟"
  prerequisite="理解 Agent 的最小闭环"
  summary="模型并不会直接执行函数。真正的 Tool Use 是一条完整链路：模型生成结构化调用意图，宿主程序执行动作，再把结果回注到上下文中。"
/>

## 模型不会真的调用函数

模型只能输出文本或结构化数据。

真正执行函数、发请求、读文件、写文件、访问浏览器的是宿主程序。

这是理解 Tool Use 的第一步：模型负责提出“行动意图”，宿主负责把这个意图变成真实操作。

## 完整链路

1. 模型判断需要外部行动
2. 模型输出结构化调用请求
3. 宿主程序解析并执行
4. 执行结果重新进入上下文

如果缺少后两步，模型只是“建议你调用某个函数”，还没有真正行动。

## 为什么 Tool Use 这么关键

因为一旦模型能稳定借助外部工具，它的能力边界会明显扩展。

它不再只是解释、总结和续写，还可以：

- 查询外部数据
- 读取项目文件
- 调用 API
- 运行代码
- 修改环境中的对象

这也是为什么 Tool Use 往往是 Agent 从“能回答”到“能做事”的分水岭。

## Tool Use 的真实职责分工

### 模型负责什么

- 判断是否需要调用工具
- 选择合适工具
- 组织参数
- 根据返回结果决定下一步

### 宿主程序负责什么

- 暴露工具定义
- 校验参数
- 执行真实动作
- 处理错误与权限
- 将结果回注到上下文

把这两个角色分清楚之后，很多系统问题就更容易定位了。

## 一个最小示例

下面这个例子用最简单的方式展示“模型请求 -> 宿主执行 -> 返回结果”的结构。

```python
tool_call = {
    "name": "read_file",
    "arguments": {
        "path": "README.md"
    }
}

def run_tool(call: dict) -> str:
    if call["name"] == "read_file":
        path = call["arguments"]["path"]
        return f"已读取文件: {path}"
    raise ValueError("unknown tool")

tool_result = run_tool(tool_call)
print(tool_result)
```

真实 Agent 当然会复杂得多，但链路本质没有变化：

- 模型输出调用请求
- 宿主执行
- 返回结果
- 模型继续判断

## 为什么工具设计会直接影响效果

Tool Use 的问题往往不在“模不会不会调”，而在工具本身是否容易被正确理解和调用。

常见问题包括：

- 工具职责太大，一次做太多事
- 参数命名模糊
- 错误信息不可读
- 工具有副作用，但没有清晰边界

这些问题都会让模型在推理时更容易误用工具。

## 常见失败模式

### 模型反复调用同一个工具

通常说明结果没有真正改变它的判断，或者上下文没有清楚记录“已经做过什么”。

### 参数组织错误

通常说明工具描述不够清晰，或者字段设计不适合模型推理。

### 调用成功但系统仍然失败

这往往说明问题不在工具执行，而在结果回注和后续状态更新。

## 工程启示

真正稳定的 Tool Use，不是“接上 function calling 接口”就结束了。

你还需要设计：

- 工具粒度
- 参数结构
- 错误处理
- 重试策略
- 权限控制
- 执行结果的记录方式

所以 Tool Use 本质上不是提示词技巧，而是一类接口设计问题。

## 下一步建议

继续阅读 [Context Engineering](./context-engineering)。

因为工具返回结果最终还是要进入上下文，才能真正影响下一轮推理。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Tool Use 的价值不在于模型会调用函数，而在于模型、宿主程序和执行结果之间形成了一个可迭代的行动闭环。
  </p>
</div>
