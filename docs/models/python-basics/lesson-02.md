---
title: 数据类型与变量
description: 学习字符串、列表、字典等核心数据结构，为文本处理和结构化数据处理打基础
---

# 第2期：数据类型与变量

如果说第 1 期解决的是“代码能跑起来”，那么这一期解决的就是“数据怎么放、怎么改、怎么传”。

在 AI 学习里，很多工作本质上都是在处理不同形态的数据：

- 一段提示词
- 一组样本列表
- 一条 JSON 结果
- 一批标签、分数、配置项

因此，字符串、列表、字典这些基础数据结构非常重要。

## 本节目标

- 理解常见基础类型和容器类型
- 熟练处理字符串
- 掌握列表、元组、字典、集合的核心用法
- 学会类型转换与类型检查
- 能将这些类型映射到真实 AI 场景中

## 数值类型

### 整数与浮点数

```python
sample_count = 128
temperature = 0.2
learning_rate = 0.001

print(type(sample_count))
print(type(temperature))
```

在 AI 场景里：

- `int` 常用于样本数、批次编号、最大长度
- `float` 常用于分数、概率、学习率、温度参数

### 布尔值

```python
use_cache = True
has_error = False
```

布尔值常用于开关型配置，例如是否启用缓存、是否打印日志。

## 字符串

字符串是这一节最重要的类型之一，因为你后面会一直处理：

- 提示词
- 标签文本
- 用户输入
- 模型输出
- 路径和配置项

### 创建与基本操作

```python
prompt = "请总结下面的文章"
topic = "机器学习"

full_prompt = prompt + "，主题是：" + topic
print(full_prompt)
print(len(full_prompt))
```

### 常用方法

```python
text = "  Hello, AI Guide!  "

print(text.strip())
print(text.lower())
print(text.upper())
print(text.replace("AI Guide", "Python"))
print(text.split())
```

### f-string

推荐优先使用 `f-string`，可读性最好。

```python
model_name = "demo-model"
temperature = 0.2

message = f"当前模型: {model_name}, 温度参数: {temperature}"
print(message)
```

## 列表

列表适合保存“有顺序的一组数据”。

```python
prompts = [
    "请总结下面内容",
    "请提取关键词",
    "请判断情感倾向"
]

print(prompts[0])
print(len(prompts))
```

### 常见操作

```python
items = ["a", "b", "c"]

items.append("d")
items.insert(1, "x")
items.remove("b")

print(items)
```

列表在 AI 脚本里很常见，例如：

- 一批输入样本
- 一组提示词模板
- 一组模型输出结果

## 元组

元组和列表很像，但创建后不可修改。

```python
image_size = (224, 224)
position = (10, 20)
```

元组适合表达“不希望被改动的固定结构”，例如尺寸、坐标、配置键组。

## 字典

字典是 AI 开发里极其高频的数据结构，因为它非常适合表示结构化信息。

```python
sample = {
    "text": "Python is useful for AI.",
    "label": "positive",
    "score": 0.98
}

print(sample["text"])
print(sample["label"])
```

### 常见操作

```python
config = {
    "model": "demo-model",
    "temperature": 0.2
}

config["max_tokens"] = 512
config["temperature"] = 0.3

print(config.get("model"))
print(config.keys())
print(config.items())
```

你后面会频繁看到这种结构：

- 一条样本：`{"text": ..., "label": ...}`
- 一次推理结果：`{"prompt": ..., "response": ..., "latency": ...}`
- 一份配置：`{"model": ..., "temperature": ...}`

## 集合

集合的特点是“无序且不重复”。

```python
tags = {"nlp", "python", "agent", "python"}
print(tags)
```

集合适合做：

- 去重
- 成员判断
- 标签集合运算

```python
train_tags = {"nlp", "rag", "agent"}
eval_tags = {"agent", "benchmark"}

print(train_tags & eval_tags)
print(train_tags | eval_tags)
```

## 类型转换

```python
text_number = "123"
count = int(text_number)

score = 3.14
score_text = str(score)

chars = list("AI")
print(count, score_text, chars)
```

真实开发中，类型转换很常见，例如：

- 把命令行输入转成数字
- 把数字转成字符串拼接日志
- 把字符串拆成列表

## 类型检查

```python
value = {"text": "hello"}

print(isinstance(value, dict))
print(isinstance(value, str))
```

在处理外部输入或 JSON 数据时，先做类型检查会更稳妥。

## 常用内置函数

```python
numbers = [3, 1, 4, 1, 5]

print(len(numbers))
print(max(numbers))
print(min(numbers))
print(sum(numbers))
print(sorted(numbers))
```

### `enumerate` 与 `zip`

```python
texts = ["a", "b", "c"]

for index, text in enumerate(texts):
    print(index, text)

names = ["sample1", "sample2"]
scores = [0.8, 0.9]

for name, score in zip(names, scores):
    print(name, score)
```

### `map` 与 `filter`

```python
texts = [" a ", " b ", "   "]

cleaned = list(map(str.strip, texts))
non_empty = list(filter(bool, cleaned))

print(cleaned)
print(non_empty)
```

## AI 场景示例：组织一批文本样本

```python
samples = [
    {"text": "Python is easy to learn.", "label": "positive"},
    {"text": "The response is too slow.", "label": "negative"},
    {"text": "Great explanation for beginners.", "label": "positive"},
]

texts = [sample["text"] for sample in samples]
labels = [sample["label"] for sample in samples]

print(texts)
print(labels)
```

这个例子看起来简单，但已经非常接近后续的数据集处理流程。

## 常见错误

### 1. 把字符串当列表修改

```python
text = "hello"
# text[0] = "H"
```

字符串不可变，这样会报错。

### 2. 直接访问不存在的字典键

```python
sample = {"text": "hello"}
print(sample["label"])
```

如果键不存在会报错，很多时候可以先用 `get()`。

### 3. 把列表和字典职责混淆

- 列表适合存“一组元素”
- 字典适合存“带字段的结构”

如果一条样本里有多个属性，通常更适合用字典。

## 练习建议

### 基础练习

1. 练习字符串的 `strip`、`split`、`replace`
2. 创建一个列表并练习增删改查
3. 创建一个字典保存个人信息并读取字段

### AI 导向练习

1. 定义一个字典保存模型配置，例如 `model`、`temperature`、`max_tokens`
2. 构造一个包含多条样本的列表，每条样本都是字典
3. 统计一组文本中每条文本的长度，并保存为新的列表

## 本节小结

- 字符串、列表、字典是后续 AI 学习里最常见的数据结构
- 字典特别适合表示样本、配置和结果
- 列表特别适合表示一批数据
- 这一节打好了，后面做文本处理、JSON 读写和模型调用会轻松很多

下一节会进入控制流与函数。到那里你就可以开始写真正的批处理脚本，而不仅仅是保存数据。

---

## 分页导航

[← 第1期：Python 环境搭建与基础语法](./lesson-01) [第3期：控制流与函数](./lesson-03) →
