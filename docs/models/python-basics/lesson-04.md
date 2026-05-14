---
title: 面向对象编程基础
description: 学习类、对象、继承与封装，为后续 AI 工程中的代码组织打基础
---

# 第4期：面向对象编程基础

当程序开始变复杂时，只靠一组零散函数已经不够了。你需要一种方式，把“数据”和“行为”组织到一起，这就是面向对象编程。

在 AI 开发里，这一章尤其常见。你以后会遇到很多类似对象：

- 模型客户端
- 数据样本对象
- 配置对象
- 工具类
- 任务执行器

## 本节目标

- 理解类和对象的关系
- 学会定义属性和方法
- 掌握构造函数 `__init__`
- 理解实例属性、类属性和方法类型
- 了解继承、封装和多态
- 能用类组织一个简单的 AI 场景代码

## 类与对象

可以把“类”理解为模板，把“对象”理解为按照模板创建出来的实例。

```python
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def show(self):
        print(f"{self.name}: {self.score}")

student = Student("Alice", 95)
student.show()
```

这里：

- `Student` 是类
- `student` 是对象
- `name` 和 `score` 是属性
- `show()` 是方法

## 构造函数与实例属性

`__init__` 会在创建对象时自动执行，通常用于初始化属性。

```python
class PromptTask:
    def __init__(self, topic, style):
        self.topic = topic
        self.style = style

    def build_prompt(self):
        return f"请用{self.style}风格介绍 {self.topic}"

task = PromptTask("向量数据库", "简洁")
print(task.build_prompt())
```

这类写法在后续封装提示词任务、模型参数和工具配置时会非常常见。

## 实例方法、类方法与静态方法

### 实例方法

最常见的方法类型，第一个参数通常写成 `self`。

```python
class Counter:
    def __init__(self):
        self.value = 0

    def increase(self):
        self.value += 1

counter = Counter()
counter.increase()
print(counter.value)
```

### 类属性与类方法

```python
class ModelConfig:
    provider = "openai"

    def __init__(self, model_name):
        self.model_name = model_name

    @classmethod
    def default(cls):
        return cls("gpt-4o-mini")

config = ModelConfig.default()
print(config.provider, config.model_name)
```

### 静态方法

静态方法不依赖对象状态，也不依赖类状态，更像是“和这个类相关的一组工具函数”。

```python
class TextUtils:
    @staticmethod
    def normalize(text):
        return text.strip().lower()

print(TextUtils.normalize("  Hello AI  "))
```

## 封装

封装不是把东西“藏起来”而已，而是让对象对外暴露稳定接口，内部细节可以后续调整。

```python
class DatasetRecord:
    def __init__(self, text):
        self._text = text

    def get_text(self):
        return self._text.strip()

record = DatasetRecord("  sample text  ")
print(record.get_text())
```

Python 没有严格私有属性机制，但以下划线开头是一种约定，表示“这是内部属性，不建议随意直接修改”。

## 继承

继承允许你在已有类的基础上扩展能力。

```python
class BaseLoader:
    def load(self):
        raise NotImplementedError("子类需要实现 load 方法")


class JsonLoader(BaseLoader):
    def load(self):
        return "读取 JSON 数据"


class CsvLoader(BaseLoader):
    def load(self):
        return "读取 CSV 数据"

print(JsonLoader().load())
print(CsvLoader().load())
```

## 多态

多态指的是：相同的调用方式，对不同对象会有不同表现。

```python
def run_loader(loader):
    print(loader.load())

run_loader(JsonLoader())
run_loader(CsvLoader())
```

这在后续做“统一接口，不同实现”时非常有用。例如：

- 不同模型供应商的客户端
- 不同数据格式的读取器
- 不同工具的执行器

## 魔术方法

魔术方法可以让你的对象更像 Python 内置对象。

```python
class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def __repr__(self):
        return f"Message(role={self.role!r}, content={self.content!r})"

message = Message("user", "请总结这段内容")
print(message)
```

在调试数据对象、日志对象和中间结果时，`__repr__` 非常实用。

## AI 场景示例：封装一个最小模型客户端

这一节最重要的是学会“用对象组织代码”。

```python
class SimpleLLMClient:
    def __init__(self, model_name, temperature=0.2):
        self.model_name = model_name
        self.temperature = temperature

    def build_payload(self, prompt):
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "prompt": prompt,
        }

    def call(self, prompt):
        payload = self.build_payload(prompt)
        return f"模拟调用完成: {payload}"


client = SimpleLLMClient("demo-model")
print(client.call("请解释什么是向量检索"))
```

这里虽然没有真的请求 API，但已经体现了对象的价值：

- 配置被收拢到一个对象里
- 请求前的数据构造有了清晰入口
- 后续更容易扩展日志、异常处理和重试机制

## 常见错误

### 1. 忘记写 `self`

```python
class Demo:
    def show():
        print("wrong")
```

实例方法必须显式接收 `self`。

### 2. 在类外访问不存在的属性

```python
class User:
    def __init__(self, name):
        self.name = name

user = User("Tom")
print(user.age)
```

这会抛出属性错误，因为 `age` 并没有定义。

### 3. 把类当作函数堆积容器

如果一个类只是简单包装若干互不相关的函数，而几乎不保存状态，那它可能更适合写成普通函数或模块。

## 练习建议

### 基础练习

1. 定义一个 `Book` 类，包含书名、作者和显示方法
2. 定义一个 `Rectangle` 类，计算面积和周长
3. 定义一个 `Account` 类，实现存款和取款逻辑

### AI 导向练习

1. 定义一个 `PromptTemplate` 类，用于格式化不同主题的提示词
2. 定义一个 `DatasetItem` 类，保存文本、标签和长度信息
3. 定义一个 `BaseModelClient` 和两个子类，模拟不同模型的调用方式

## 本节小结

- 类是组织数据与行为的方式
- 对象让状态和方法绑定在一起
- 继承和多态让代码更容易扩展
- 面向对象是后续理解 AI 工程代码结构的重要基础

下一节会进入文件操作、异常处理和模块组织。那一节会更贴近真实开发，因为大多数 AI 项目都离不开文件、配置、JSON 和错误处理。

---

## 分页导航

[← 第3期：控制流与函数](./lesson-03) [第5期：文件操作与异常处理](./lesson-05) →
