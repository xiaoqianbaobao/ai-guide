---
title: Python 环境搭建与基础语法
description: 为后续数据处理、模型调用和 AI 工程脚本准备 Python 运行环境与基础语法
---

# 第1期：Python 环境搭建与基础语法

这节课的目标不是停留在“装好 Python”，而是把你带到一个能真正开始写代码、跑脚本、处理文件的状态。

后面无论你要做数据清洗、模型调用，还是写 Agent 工具，第一步都离不开稳定的本地环境和最基本的语法习惯。

## 本节目标

- 理解为什么 AI 学习通常以 Python 为起点
- 安装并验证 Python 与 `pip`
- 学会使用终端运行 Python 脚本
- 掌握变量、基本数据类型和常用运算符
- 建立清晰、可维护的基础代码习惯

## 为什么 AI 学习常用 Python

Python 在 AI 领域被广泛使用，核心原因不是“它最先进”，而是它足够适合学习和快速实现：

- 语法简洁，适合快速上手
- 生态成熟，数据处理和模型工具丰富
- 适合写脚本、实验代码和工具程序
- 在数据科学、机器学习、推理服务和自动化领域都有广泛应用

对于初学者来说，Python 最重要的价值是：你可以更快地把注意力放在问题本身，而不是被语言细节拖住。

## 环境搭建

### Windows

最简单的方式是用官方安装包或 `winget`。

```powershell
winget install Python.Python.3.11
```

安装时建议确认两点：

- 已将 Python 加入 PATH
- 安装了 `pip`

### macOS

推荐使用 `Homebrew`：

```bash
brew install python
```

### Linux

以 Ubuntu / Debian 为例：

```bash
sudo apt update
sudo apt install python3 python3-pip
```

## 验证安装

安装完成后，在终端中执行：

```bash
python --version
pip --version
```

如果你的系统中 `python` 不可用，可以尝试：

```bash
python3 --version
pip3 --version
```

## 建议的开发习惯

从这一节开始，建议同时培养几个习惯：

- 习惯用终端运行脚本
- 习惯把代码保存为 `.py` 文件，而不是只在解释器里临时试
- 习惯为文件和变量起清晰的名字
- 习惯在报错时先读错误信息，而不是直接放弃

## 第一个 Python 程序

创建一个 `hello.py`：

```python
print("Hello, Python!")
```

运行方式：

```bash
python hello.py
```

你会看到：

```text
Hello, Python!
```

这一步看起来简单，但它意味着：

- 你的环境已经正确安装
- 你知道如何执行一个脚本
- 你可以开始进入真正的代码练习

## 交互式解释器

Python 也提供交互式环境，适合快速试验。

```bash
python
```

例如：

```python
>>> 2 + 3
5
>>> print("AI Guide")
AI Guide
```

交互式环境适合验证小片段代码，但正式学习时仍建议优先写进 `.py` 文件。

## 变量与基本数据类型

### 变量

变量可以理解为“带名字的数据”。

```python
name = "Alice"
age = 18
temperature = 0.2
```

### 命名规则

- 只能包含字母、数字和下划线
- 不能以数字开头
- 不能使用 Python 关键字
- 推荐用有语义的英文名

```python
user_name = "alice"
max_tokens = 512
model_name = "demo-model"
```

这种命名方式在后续 AI 项目里也更自然，因为你会频繁接触 `prompt`、`temperature`、`dataset_path` 这类变量。

### 常见基础类型

#### 整数 `int`

```python
count = 10
year = 2026
```

#### 浮点数 `float`

```python
score = 0.95
learning_rate = 0.001
```

#### 字符串 `str`

```python
text = "hello"
prompt = "请总结下面的内容"
```

#### 布尔值 `bool`

```python
is_ready = True
has_error = False
```

## 基本运算符

### 算术运算

```python
a = 10
b = 3

print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a // b)
print(a % b)
print(a ** b)
```

### 比较运算

```python
print(5 > 3)
print(5 == 5)
print(5 != 2)
```

### 逻辑运算

```python
is_python_ready = True
has_pip = True

print(is_python_ready and has_pip)
print(is_python_ready or False)
print(not False)
```

## 注释与基础规范

### 单行注释

```python
# 这是注释
print("hello")
```

### 文档字符串

```python
def greet(name):
    """返回一条简单问候语。"""
    return f"Hello, {name}"
```

### 基础规范建议

- 保持缩进一致
- 不要把一行写得过长
- 变量名尽量表达含义
- 示例代码优先追求清晰，再追求“高级技巧”

## AI 场景示例：准备一个最小实验脚本

从现在开始，尽量用更接近未来 AI 开发的变量名和例子。

```python
model_name = "demo-model"
temperature = 0.3
prompt = "请解释什么是监督学习"

print("模型名称:", model_name)
print("温度参数:", temperature)
print("提示词:", prompt)
```

虽然这里只是打印，但它已经接近后续真实代码的形态：有配置、有输入、有参数。

## 常见错误

### 1. 没有配置 PATH

如果终端提示找不到 `python`，通常说明安装成功但环境变量没有配置好。

### 2. 中英文符号混用

```python
print（"hello"）
```

这类全角括号会导致语法错误。

### 3. 变量名含义不清

```python
a = "demo-model"
b = 0.2
```

建议改成：

```python
model_name = "demo-model"
temperature = 0.2
```

## 练习建议

### 基础练习

1. 在本机完成 Python 与 `pip` 安装验证
2. 创建并运行一个 `hello.py`
3. 定义 4 个不同类型的变量并打印它们

### AI 导向练习

1. 创建变量保存 `model_name`、`temperature`、`prompt`
2. 编写一个脚本打印“当前实验配置”
3. 尝试用字符串保存一段提示词，并打印其长度

## 本节小结

- Python 是后续 AI 学习中最重要的基础工具之一
- 能稳定运行脚本，比记住很多概念更重要
- 变量、基础类型和运算符会在后续每一节反复使用
- 从第一节开始养成清晰命名和规范书写的习惯，会让后面轻松很多

下一节会进入数据类型与容器。那一节会更贴近真实 AI 场景，因为文本、列表、字典和结构化数据会频繁出现。

---

## 分页导航

[第2期：数据类型与变量](./lesson-02) →
