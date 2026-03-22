---
title: Python环境搭建与基础语法
description: 学习Python发展历史、环境搭建以及基础语法知识
---

# 第1期：Python环境搭建与基础语法

## 📖 学习目标

- 了解Python语言的发展历史与核心特点
- 掌握Python环境的安装与配置方法
- 熟悉Python基础语法结构
- 能够编写并运行简单的Python程序

## 🎯 Python语言概述

### 历史背景

Python由吉多·范罗苏姆（Guido van Rossum）于1989年创造，1991年首次发布。Python的设计哲学强调代码的可读性和简洁性，其名称来源于英国喜剧团体Monty Python。

### 核心特点

1. **简洁易读**：语法清晰，代码结构简单
2. **跨平台**：支持Windows、macOS、Linux等多种操作系统
3. **开源免费**：完全开源，可自由使用和修改
4. **功能强大**：丰富的标准库和第三方库
5. **应用广泛**：涵盖Web开发、数据科学、人工智能、自动化等多个领域

### 与其他语言的比较

| 特性 | Python | Java | C++ |
|------|--------|------|-----|
| 学习难度 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 执行速度 | 中等 | 快 | 最快 |
| 代码量 | 少 | 多 | 多 |
| 应用领域 | 广泛 | 企业级 | 系统编程 |

## 🛠️ 环境搭建

### Windows环境安装

#### 方法一：官方安装包

1. 访问Python官网下载页面：https://www.python.org/downloads/
2. 下载适合Windows的安装包（推荐下载最新稳定版本）
3. 运行安装程序，勾选"Add Python to PATH"选项
4. 完成安装后，在命令行中输入`python --version`验证安装

#### 方法二：使用包管理器

```bash
# 使用winget（Windows 10+）
winget install Python.Python.3.11

# 使用Chocolatey
choco install python
```

### macOS环境安装

#### 使用Homebrew（推荐）

```bash
# 安装Homebrew（如果尚未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Python
brew install python
```

#### 官方安装包

1. 访问Python官网下载macOS版本
2. 运行.dmg安装包
3. 按照安装向导完成安装

### Linux环境安装

#### Ubuntu/Debian系统

```bash
sudo apt update
sudo apt install python3 python3-pip
```

#### CentOS/RHEL系统

```bash
sudo yum install python3 python3-pip
```

#### Fedora系统

```bash
sudo dnf install python3 python3-pip
```

### 验证安装

在终端中执行以下命令验证安装是否成功：

```bash
# 检查Python版本
python --version
# 或
python3 --version

# 检查pip版本
pip --version
# 或
pip3 --version
```

## 📝 第一个Python程序

### Hello World程序

创建一个名为`hello.py`的文件，输入以下代码：

```python
# 这是一个简单的Hello World程序
print("Hello, World!")
```

**代码解释：**
- `#` 后面的内容是注释，会被Python解释器忽略
- `print()` 是Python内置函数，用于输出内容到控制台

### 运行程序

在终端中执行以下命令：

```bash
python hello.py
# 或
python3 hello.py
```

预期输出：
```
Hello, World!
```

### 交互式解释器

Python还提供了交互式解释器（REPL），可以直接输入代码并立即看到结果：

```bash
python
# 或
python3
```

进入交互式模式后，你可以直接输入Python代码：

```python
>>> print("Hello, Python!")
Hello, Python!
>>> 2 + 2
4
>>> exit()
```

## 🏷️ 变量与基本数据类型

### 变量的概念

变量是存储数据的容器。在Python中，变量不需要预先声明类型，解释器会自动推断。

### 变量命名规则

1. 只能包含字母、数字和下划线
2. 不能以数字开头
3. 不能使用Python关键字
4. 区分大小写

**合法的变量名：**
```python
name = "张三"
age = 25
_height = 1.75
user_name = "user123"
```

**非法的变量名：**
```python
# 2name = "张三"  # 错误：不能以数字开头
# class = "Python"  # 错误：不能使用关键字
# user-name = "张三"  # 错误：不能使用连字符
```

### 基本数据类型

#### 整数（int）

```python
# 整数示例
positive_num = 42
negative_num = -17
zero = 0

print(type(positive_num))  # <class 'int'>
```

#### 浮点数（float）

```python
# 浮点数示例
pi = 3.14159
scientific = 1.5e-3  # 科学计数法
negative_float = -2.5

print(type(pi))  # <class 'float'>
```

#### 字符串（str）

```python
# 字符串示例
single_quote = 'Hello'
double_quote = "World"
triple_quote = """这是一个
多行字符串"""

# 字符串操作
name = "Python"
print(name.upper())  # PYTHON
print(name.lower())  # python
print(len(name))     # 6
```

#### 布尔值（bool）

```python
# 布尔值示例
is_true = True
is_false = False

print(type(is_true))  # <class 'bool'>
```

## 🔢 运算符与表达式

### 算术运算符

```python
# 基本算术运算
a = 10
b = 3

print(a + b)  # 加法: 13
print(a - b)  # 减法: 7
print(a * b)  # 乘法: 30
print(a / b)  # 除法: 3.333...
print(a // b) # 整除: 3
print(a % b)  # 取余: 1
print(a ** b) # 幂运算: 1000
```

### 比较运算符

```python
x = 5
y = 8

print(x == y)  # 等于: False
print(x != y)  # 不等于: True
print(x < y)   # 小于: True
print(x > y)   # 大于: False
print(x <= y)  # 小于等于: True
print(x >= y)  # 大于等于: False
```

### 逻辑运算符

```python
a = True
b = False

print(a and b)  # 与: False
print(a or b)   # 或: True
print(not a)    # 非: False
```

## 💬 代码注释与规范

### 单行注释

```python
# 这是单行注释
print("Hello")  # 这也是注释
```

### 多行注释

```python
"""
这是多行注释
可以跨越多行
通常用于文档字符串
"""

'''
这也是多行注释
使用单引号包裹
'''
```

### 文档字符串

```python
def calculate_area(length, width):
    """
    计算矩形面积
    
    参数:
        length (float): 矩形的长度
        width (float): 矩形的宽度
    
    返回:
        float: 矩形的面积
    """
    return length * width
```

## 🎓 练习题

### 基础练习

1. **环境验证**：在你的环境中运行Python，验证安装是否成功
2. **Hello World**：创建并运行一个Hello World程序
3. **变量练习**：创建不同类型的变量并打印它们的类型

### 编程练习

1. **计算器程序**：编写一个简单的计算器，实现加减乘除运算
2. **温度转换**：编写程序将摄氏度转换为华氏度
3. **个人资料**：创建一个程序，输入并显示个人信息

### 挑战练习

1. **斐波那契数列**：编写程序生成斐波那契数列的前n项
2. **简单加密**：实现一个简单的字符替换加密算法
3. **时间转换器**：编写程序将秒数转换为时分秒格式

## 🔗 扩展阅读

- [Python官方文档 - 语言参考](https://docs.python.org/zh-cn/3/reference/)
- [Python变量命名规范](https://pep8.org/#naming-conventions)
- [Python运算符优先级](https://docs.python.org/zh-cn/3/reference/expressions.html#operator-precedence)

---

**📝 本节小结：**

- Python是一门简洁、易读、功能强大的编程语言
- 正确安装Python环境是学习的第一步
- 掌握变量、数据类型和基本运算符是编程的基础
- 良好的代码规范和注释习惯对编程非常重要

**💡 下一节预告：** 在第2期中，我们将深入学习Python的数据类型系统，包括数值类型、字符串操作、容器类型等核心概念。