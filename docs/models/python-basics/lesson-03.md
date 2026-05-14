---
title: 控制流与函数
description: 用条件、循环和函数组织逻辑，为后续数据处理与 AI 脚本打基础
---

# 第3期：控制流与函数

控制流决定程序“怎么走”，函数决定代码“怎么组织”。

对于后续的 AI 学习来说，这一节非常关键。你以后会频繁写到：

- 按条件筛选样本
- 批量处理文本和数据
- 把模型调用逻辑封装成函数
- 在循环中处理一批输入，再汇总输出

## 本节目标

- 掌握 `if / elif / else` 的基本写法
- 熟练使用 `for` 和 `while`
- 理解 `break`、`continue`、`pass`
- 学会定义函数、传递参数和接收返回值
- 理解作用域，避免变量混乱

## 为什么这对 AI 学习重要

很多初学者以为 AI 开发只需要“会调接口”，但真正写脚本时，你往往要做这些事情：

- 遍历数据集中的每一条记录
- 按规则过滤脏数据
- 把提示词处理逻辑封装成函数
- 根据模型返回结果走不同分支

所以，控制流和函数不是单独的一章，而是后续所有 AI 代码的基础骨架。

## 条件语句

### 基本判断

```python
score = 82

if score >= 90:
    level = "excellent"
elif score >= 80:
    level = "good"
elif score >= 60:
    level = "pass"
else:
    level = "fail"

print(level)
```

### 复合条件

```python
text = "Python is useful for AI."
length_ok = len(text) > 10
has_keyword = "AI" in text

if length_ok and has_keyword:
    print("这条文本可以继续处理")
```

### 条件表达式

```python
temperature = 0.2
mode = "stable" if temperature < 0.5 else "creative"
print(mode)
```

## 循环语句

### for 循环

`for` 适合处理“已知可迭代对象”的情况，例如列表、字符串、字典和文件。

```python
prompts = [
    "请总结下面的文章",
    "请提取关键信息",
    "请给出三条建议"
]

for prompt in prompts:
    print("正在处理：", prompt)
```

### range 的使用

```python
for i in range(3):
    print(f"第 {i + 1} 次调用")

for i in range(2, 10, 2):
    print(i)
```

### while 循环

`while` 适合“条件满足就继续”的场景。

```python
retries = 0

while retries < 3:
    print("尝试执行任务")
    retries += 1
```

### break、continue、pass

```python
records = ["ok", "", "pending", "skip", "done"]

for record in records:
    if record == "":
        continue
    if record == "skip":
        break
    print(record)
```

## 函数

函数的作用是把重复逻辑打包起来，变成可以复用的能力单元。

### 基本定义

```python
def clean_text(text):
    text = text.strip()
    text = text.replace("\n", " ")
    return text

result = clean_text("  hello\nworld  ")
print(result)
```

### 参数与默认值

```python
def truncate_text(text, max_length=50):
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

print(truncate_text("Python makes AI prototyping faster.", 20))
print(truncate_text("short text"))
```

### 多个返回值

```python
def analyze_text(text):
    length = len(text)
    word_count = len(text.split())
    has_number = any(char.isdigit() for char in text)
    return length, word_count, has_number

length, word_count, has_number = analyze_text("AI guide 2026")
print(length, word_count, has_number)
```

### 可变参数

```python
def average(*numbers):
    return sum(numbers) / len(numbers)

print(average(1, 2, 3, 4))
```

## 作用域与命名空间

如果变量定义位置混乱，代码会很难维护。

```python
prefix = "AI"

def build_name(topic):
    suffix = "guide"
    return f"{prefix}-{topic}-{suffix}"

print(build_name("python"))
```

### global 和 nonlocal

大多数时候不建议滥用 `global`。更推荐把数据通过参数传入函数，再通过返回值传出来。

```python
counter = 0

def increase():
    global counter
    counter += 1
    return counter

print(increase())
```

## AI 场景示例：批量清洗提示词

下面这个例子把前面学过的条件、循环和函数放到一个更接近 AI 的任务里。

```python
raw_prompts = [
    "  帮我总结下面的新闻  ",
    "",
    "请提取三个关键词",
    "  请判断情感倾向  "
]

def normalize_prompt(text):
    text = text.strip()
    if not text:
        return None
    return text.replace("  ", " ")

clean_prompts = []

for prompt in raw_prompts:
    normalized = normalize_prompt(prompt)
    if normalized is None:
        continue
    clean_prompts.append(normalized)

print(clean_prompts)
```

这个模式以后会频繁出现：

- 先读入一批原始数据
- 用循环逐条处理
- 用条件判断过滤异常值
- 用函数封装重复逻辑

## 常见错误

### 1. 缩进不一致

```python
if True:
print("wrong")
```

`Python` 用缩进表示代码块，缩进错误会直接报错。

### 2. 循环变量和外部变量混用

```python
items = [1, 2, 3]
item = "text"

for item in items:
    print(item)
```

这样容易覆盖原来的变量名。建议变量命名保持清晰。

### 3. 函数只打印，不返回

```python
def add(a, b):
    print(a + b)
```

如果后面还要继续使用结果，应该 `return`，而不是只 `print`。

## 练习建议

### 基础练习

1. 编写程序判断一个句子是否包含指定关键词
2. 使用循环统计列表中偶数的数量
3. 写一个函数，把字符串列表统一去掉首尾空格

### AI 导向练习

1. 给定一组文本，过滤掉空文本并统计平均长度
2. 编写 `build_prompt(topic, style="brief")` 函数，按不同风格生成提示词
3. 编写一个批处理函数，对文本列表逐条调用清洗逻辑并返回结果

## 本节小结

- 条件语句控制程序走向
- 循环负责批量处理
- 函数负责复用和组织逻辑
- 这三者会在后续数据处理、模型调用和 Agent 脚本中反复出现

下一节会进入面向对象编程。它会帮助你进一步组织代码，为后面的模型客户端、配置对象和工具类做铺垫。

---

## 分页导航

[← 第2期：数据类型与变量](./lesson-02) [第4期：面向对象编程基础](./lesson-04) →
