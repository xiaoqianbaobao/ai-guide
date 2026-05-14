---
title: 文件操作与异常处理
description: 学习文件、JSON、模块和错误处理，为数据集与模型调用脚本打基础
---

# 第5期：文件操作与异常处理

从这一节开始，Python 会明显更接近真实开发。

因为大多数 AI 项目里，你都要做这些事情：

- 读取数据集文件
- 读写 JSON 配置
- 保存模型输出结果
- 处理接口报错和数据异常
- 把脚本整理成模块

## 本节目标

- 掌握文本文件与 JSON 文件的读写
- 理解 `try / except / else / finally`
- 学会使用 `with` 管理资源
- 了解模块与包的基本组织方式
- 为后续数据处理、模型调用与小工具开发打基础

## 文件操作

### 基本读写

```python
with open("example.txt", "w", encoding="utf-8") as file:
    file.write("hello python\n")
    file.write("this is a file example\n")

with open("example.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)
```

### 按行读取

对于较大的文本文件，按行处理通常更稳妥。

```python
with open("prompts.txt", "r", encoding="utf-8") as file:
    for line in file:
        prompt = line.strip()
        if not prompt:
            continue
        print(prompt)
```

### 追加写入

```python
with open("run.log", "a", encoding="utf-8") as file:
    file.write("task finished\n")
```

## 路径处理

推荐优先使用 `pathlib`，比 `os.path` 更直观。

```python
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

file_path = data_dir / "samples.txt"
file_path.write_text("sample one\nsample two\n", encoding="utf-8")

print(file_path.read_text(encoding="utf-8"))
print(file_path.exists())
```

## JSON 读写

JSON 是 AI 项目里最常见的数据格式之一，配置文件、对话记录、推理结果都很常见。

```python
import json

config = {
    "model": "demo-model",
    "temperature": 0.2,
    "max_tokens": 512
}

with open("config.json", "w", encoding="utf-8") as file:
    json.dump(config, file, ensure_ascii=False, indent=2)

with open("config.json", "r", encoding="utf-8") as file:
    loaded_config = json.load(file)

print(loaded_config)
```

## 异常处理

异常不是“程序出错才学”，而是为了让程序在遇到问题时仍然可控。

### 基本结构

```python
try:
    value = int("abc")
except ValueError:
    print("输入内容不能转换为整数")
```

### 完整结构

```python
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("除数不能为 0")
    else:
        print("计算成功")
        return result
    finally:
        print("本次计算结束")

divide(10, 2)
```

### 捕获并重新抛出异常

```python
def load_json(path):
    import json

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as error:
        raise RuntimeError(f"文件不存在: {path}") from error
```

## 上下文管理器

`with` 的核心作用是：进入代码块时申请资源，退出时自动释放资源。

```python
with open("result.txt", "w", encoding="utf-8") as file:
    file.write("done")
```

这比手动 `open()` 再 `close()` 更安全，尤其在异常发生时。

## 模块与包

当代码变多时，应把不同职责拆到不同文件中。

### 一个简单模块

假设你有一个 `text_utils.py`：

```python
def clean_text(text):
    return text.strip().replace("\n", " ")


def is_empty(text):
    return clean_text(text) == ""
```

在其他文件中可以这样使用：

```python
import text_utils

print(text_utils.clean_text("  hello\nworld  "))
```

也可以这样导入：

```python
from text_utils import clean_text

print(clean_text("  demo text  "))
```

### 包的基本结构

```text
project/
  app.py
  utils/
    __init__.py
    io.py
    prompts.py
```

这样拆分以后，代码会更容易维护，也更接近真实工程目录。

## AI 场景示例：读取数据集并保存推理结果

下面这个例子把文件、JSON、异常处理和函数组织串起来。

```python
import json
from pathlib import Path


def load_samples(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_results(file_path, results):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)


def run_pipeline():
    input_path = Path("samples.json")
    output_path = Path("results.json")

    try:
        samples = load_samples(input_path)
        results = []

        for sample in samples:
            text = sample["text"].strip()
            results.append({
                "text": text,
                "length": len(text),
            })

        save_results(output_path, results)
        print("处理完成")
    except FileNotFoundError:
        print("输入文件不存在，请先准备数据集")
    except KeyError:
        print("样本格式错误，缺少 text 字段")


run_pipeline()
```

这个例子已经非常接近真实的 AI 脚本：

- 读入数据集
- 逐条处理样本
- 生成结构化结果
- 保存输出文件
- 对常见错误给出清晰提示

## 常用标准库建议

下面这些库在后续学习中会经常出现：

- `json`：处理配置和结构化结果
- `pathlib`：处理路径和目录
- `datetime`：记录时间和生成日志名
- `collections`：做计数和简单数据结构辅助
- `logging`：记录运行信息和错误

## 常见错误

### 1. 忘记指定编码

```python
with open("data.txt", "r") as file:
    content = file.read()
```

遇到中文文本时，最好显式写上 `encoding="utf-8"`。

### 2. 异常捕获太宽泛

```python
try:
    ...
except Exception:
    print("出错了")
```

这会让调试变困难。优先捕获具体异常类型。

### 3. 文件路径写死

```python
with open("C:/Users/xxx/Desktop/data.json", "r", encoding="utf-8") as file:
    ...
```

更推荐使用相对路径或 `pathlib` 统一管理。

## 练习建议

### 基础练习

1. 读取一个文本文件，统计总行数与非空行数
2. 编写一个函数，把字典保存为 JSON 文件
3. 编写一个安全读取函数，文件不存在时给出提示

### AI 导向练习

1. 读取一个包含 `text` 字段的 JSON 列表，统计每条文本长度
2. 编写一个配置加载器，从 `config.json` 读取模型参数
3. 编写一个结果保存脚本，把文本、标签和分数写入 JSON 文件

## 课程总结

完成前 5 期后，你已经建立了后续 AI 学习最重要的 Python 基础：

1. 会搭建并运行 Python 环境
2. 会处理常见数据类型与容器
3. 会用控制流和函数组织逻辑
4. 会用类和对象组织代码
5. 会处理文件、JSON、模块和异常

接下来最适合进入的方向是：

1. `NumPy` 和 `Pandas`
2. 数据清洗与分析
3. 模型 API 调用与结果处理
4. AI 工程与 Agent 开发实践

## 分页导航

[← 第4期：面向对象编程基础](./lesson-04)
