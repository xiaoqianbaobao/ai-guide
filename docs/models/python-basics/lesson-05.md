---
title: 文件操作与异常处理
description: 学习Python的文件操作、异常处理机制，以及模块与包的使用
---

# 第5期：文件操作与异常处理

## 📖 学习目标

- 掌握文件的读写操作
- 理解异常处理机制
- 学会使用上下文管理器
- 理解模块与包的概念
- 掌握常用标准库的使用

## 📁 文件操作

### 文件的打开与关闭

```python
# 基本文件操作
def basic_file_operations():
    # 写入文件
    with open("example.txt", "w", encoding="utf-8") as file:
        file.write("Hello, Python!\n")
        file.write("这是第二行\n")
    
    # 读取文件
    with open("example.txt", "r", encoding="utf-8") as file:
        content = file.read()
        print("文件内容:")
        print(content)
    
    # 追加写入
    with open("example.txt", "a", encoding="utf-8") as file:
        file.write("这是追加的内容\n")

basic_file_operations()
```

### 文件读取方法

```python
# 准备测试文件
with open("test.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n第二行\n第三行\n第四行\n第五行")

# read() - 读取整个文件
with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print("read()结果:", repr(content))

# readline() - 读取单行
with open("test.txt", "r", encoding="utf-8") as f:
    line1 = f.readline()
    line2 = f.readline()
    print("readline()结果:")
    print(repr(line1))
    print(repr(line2))

# readlines() - 读取所有行
with open("test.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    print("readlines()结果:")
    print(lines)

# 迭代读取
with open("test.txt", "r", encoding="utf-8") as f:
    print("迭代读取:")
    for i, line in enumerate(f, 1):
        print(f"第{i}行: {line.strip()}")
```

### 文件写入方法

```python
# 写入方法对比
data = ["第一行\n", "第二行\n", "第三行\n"]

# write() - 写入字符串
with open("write_test1.txt", "w", encoding="utf-8") as f:
    f.write("单个字符串写入\n")

# writelines() - 写入列表
with open("write_test2.txt", "w", encoding="utf-8") as f:
    f.writelines(data)

# 格式化写入
with open("write_test3.txt", "w", encoding="utf-8") as f:
    for i, line in enumerate(data, 1):
        f.write(f"第{i}行: {line}")
```

### 二进制文件操作

```python
# 二进制文件读写
def binary_file_operations():
    # 写入二进制数据
    data = b"Hello Binary World!"
    with open("binary_test.bin", "wb") as f:
        f.write(data)
    
    # 读取二进制数据
    with open("binary_test.bin", "rb") as f:
        binary_content = f.read()
        print("二进制内容:", binary_content)
        print("解码后:", binary_content.decode('utf-8'))

binary_file_operations()
```

### 文件路径操作

```python
import os
import glob

# 获取当前目录
current_dir = os.getcwd()
print("当前目录:", current_dir)

# 列出目录内容
files = os.listdir(".")
print("目录内容:", files)

# 文件路径拼接
file_path = os.path.join(current_dir, "test.txt")
print("完整路径:", file_path)

# 文件信息
file_info = os.stat("test.txt")
print("文件大小:", file_info.st_size, "字节")
print("修改时间:", file_info.st_mtime)

# 搜索文件
txt_files = glob.glob("*.txt")
print("所有txt文件:", txt_files)
```

## ⚠️ 异常处理机制

### try-except语句

```python
# 基本异常处理
def handle_exceptions():
    try:
        # 可能出错的代码
        num = int(input("请输入一个数字: "))
        result = 10 / num
        print(f"结果: {result}")
    
    except ValueError:
        # 处理特定异常
        print("输入错误：请输入一个有效的数字")
    
    except ZeroDivisionError:
        print("错误：不能除以零")
    
    except Exception as e:
        # 处理其他异常
        print(f"发生未知错误: {e}")
    
    else:
        # 没有异常时执行
        print("计算成功完成")
    
    finally:
        # 总是执行
        print("程序执行完毕")

# handle_exceptions()
```

### 异常链与自定义异常

```python
# 自定义异常
class CustomError(Exception):
    """自定义异常类"""
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code

# 异常链
def process_data(data):
    try:
        if not isinstance(data, list):
            raise TypeError("数据必须是列表类型")
        
        if len(data) == 0:
            raise CustomError("数据列表不能为空", error_code=1001)
        
        # 处理数据
        result = sum(data) / len(data)
        return result
    
    except Exception as e:
        # 重新抛出异常，保留原始异常信息
        raise RuntimeError(f"处理数据时发生错误: {e}") from e

# 使用自定义异常
try:
    result = process_data("not a list")
except RuntimeError as e:
    print(f"捕获异常: {e}")
    print(f"原始异常: {e.__cause__}")
```

### 上下文管理器

```python
# 自定义上下文管理器
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        print(f"打开文件: {self.filename}")
        self.file = open(self.filename, self.mode, encoding="utf-8")
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"关闭文件: {self.filename}")
        if self.file:
            self.file.close()
        
        # 返回False表示不抑制异常
        if exc_type:
            print(f"发生异常: {exc_type.__name__}: {exc_val}")
        return False

# 使用上下文管理器
with FileManager("context_test.txt", "w") as f:
    f.write("使用上下文管理器写入\n")
    # f.write(123)  # 这会引发异常

# 内置上下文管理器
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start_time = time.time()
    print("开始计时")
    yield
    end_time = time.time()
    print(f"耗时: {end_time - start_time:.2f}秒")

with timer():
    print("执行一些操作")
    import time
    time.sleep(1)
```

## 📦 模块与包

### 模块的创建与导入

```python
# 创建一个简单的模块 math_utils.py
math_utils_content = '''
"""
数学工具模块
包含一些常用的数学函数
"""

import math

def factorial(n):
    """计算阶乘"""
    if n < 0:
        raise ValueError("阶乘不能为负数")
    return math.factorial(n)

def is_prime(n):
    """判断是否为质数"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def fibonacci(n):
    """生成斐波那契数列的前n项"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[i-1] + fib_sequence[i-2])
    return fib_sequence

# 常量
PI = math.pi
E = math.e
'''

# 写入模块文件
with open("math_utils.py", "w", encoding="utf-8") as f:
    f.write(math_utils_content)

# 导入模块
import math_utils
import math_utils as mu

# 使用模块
print(f"5! = {math_utils.factorial(5)}")
print(f"17是质数吗? {math_utils.is_prime(17)}")
print(f"斐波那契数列前10项: {math_utils.fibonacci(10)}")

# 导入特定函数
from math_utils import factorial, fibonacci
print(f"10! = {factorial(10)}")
print(f"斐波那契数列前8项: {fibonacci(8)}")
```

### 包的结构

```python
# 创建包结构
package_structure = {
    "mypackage/__init__.py": '''
"""
mypackage 包
"""

__version__ = "1.0.0"
__author__ = "Python Developer"

from . import utils
from . import data

__all__ = ["utils", "data"]
''',
    
    "mypackage/utils.py": '''
"""
工具模块
"""

def format_string(text, style="upper"):
    """格式化字符串"""
    if style == "upper":
        return text.upper()
    elif style == "lower":
        return text.lower()
    elif style == "title":
        return text.title()
    else:
        return text

def calculate_average(numbers):
    """计算平均值"""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
''',
    
    "mypackage/data.py": '''
"""
数据处理模块
"""

def load_data(filename):
    """加载数据"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

def save_data(filename, data):
    """保存数据"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)
    return True
'''
}

# 创建包文件
import os
os.makedirs("mypackage", exist_ok=True)

for file_path, content in package_structure.items():
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# 导入包
import mypackage
from mypackage import utils, data

# 使用包
print(utils.format_string("hello world", "title"))
print(utils.calculate_average([1, 2, 3, 4, 5]))
```

## 🛠️ 常用标准库

### os模块

```python
import os

# 目录操作
print("当前工作目录:", os.getcwd())
os.makedirs("test_dir", exist_ok=True)
os.chdir("test_dir")
print("切换后目录:", os.getcwd())

# 文件操作
with open("test.txt", "w") as f:
    f.write("测试内容")

# 路径操作
print("文件路径:", os.path.abspath("test.txt"))
print("目录名:", os.path.dirname(os.path.abspath("test.txt")))
print("文件名:", os.path.basename(os.path.abspath("test.txt")))

# 系统信息
print("操作系统:", os.name)
print("环境变量:", os.environ.get("PATH", "无PATH环境变量"))

# 删除文件和目录
os.remove("test.txt")
os.rmdir("test_dir")
```

### sys模块

```python
import sys

# 获取Python版本
print(f"Python版本: {sys.version}")
print(f"Python版本信息: {sys.version_info}")

# 获取命令行参数
print("命令行参数:", sys.argv)

# 获取模块搜索路径
print("模块搜索路径:")
for path in sys.path:
    print(f"  {path}")

# 获取标准输入输出
print("标准输出:", sys.stdout)
print("标准错误:", sys.stderr)

# 程序退出
# sys.exit("程序异常退出")
```

### json模块

```python
import json

# Python对象转JSON
data = {
    "name": "张三",
    "age": 25,
    "skills": ["Python", "JavaScript"],
    "address": {
        "city": "北京",
        "district": "朝阳区"
    }
}

# 转换为JSON字符串
json_str = json.dumps(data, ensure_ascii=False, indent=2)
print("JSON字符串:")
print(json_str)

# 保存到文件
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 从文件读取
with open("data.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)
    print("加载的数据:", loaded_data)

# JSON字符串转Python对象
json_string = '{"name": "李四", "age": 30}'
python_obj = json.loads(json_string)
print("Python对象:", python_obj)
```

### datetime模块

```python
from datetime import datetime, date, time, timedelta

# 当前时间
now = datetime.now()
print("当前时间:", now)
print("年份:", now.year)
print("月份:", now.month)
print("日期:", now.day)
print("时间:", now.time())

# 日期操作
today = date.today()
print("今天:", today)

# 时间差
future = now + timedelta(days=30)
print("30天后:", future)

# 格式化时间
print("格式化时间:", now.strftime("%Y-%m-%d %H:%M:%S"))

# 解析时间字符串
time_str = "2023-12-25 15:30:00"
parsed_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
print("解析时间:", parsed_time)
```

## 🎓 练习题

### 基础练习

1. **文件操作**：创建一个学生成绩管理程序，支持读取、写入、统计成绩
2. **异常处理**：编写一个安全的计算器程序，处理各种异常情况
3. **模块使用**：创建一个数据处理模块，包含数据清洗、统计分析等功能

### 编程练习

1. **日志系统**：实现一个简单的日志记录系统，支持不同级别日志
2. **配置管理**：创建一个配置文件管理器，支持JSON、INI格式
3. **数据备份**：编写一个文件备份工具，支持定时备份和增量备份

### 挑战练习

1. **文件监控**：实现一个文件监控系统，实时监控文件变化
2. **数据迁移**：创建一个数据库迁移工具，支持数据格式转换
3. **性能测试**：编写一个性能测试框架，测试代码执行效率

## 🔗 扩展阅读

- [Python官方文档 - 文件操作](https://docs.python.org/zh-cn/3/tutorial/inputoutput.html)
- [Python官方文档 - 异常处理](https://docs.python.org/zh-cn/3/tutorial/errors.html)
- [Python官方文档 - 模块](https://docs.python.org/zh-cn/3/tutorial/modules.html)
- [Python官方文档 - 标准库](https://docs.python.org/zh-cn/3/library/)

---

**📝 本节小结：**

- 文件操作是数据持久化的基础，需要掌握读写方法和异常处理
- 异常处理机制使程序更加健壮，能够优雅地处理错误情况
- 上下文管理器提供了资源管理的统一接口，确保资源正确释放
- 模块和包是代码组织的重要方式，提高代码的可维护性
- 标准库提供了丰富的功能，减少重复开发

**💡 课程总结：**

恭喜你完成了Python基础教程的全部5期内容！通过系统学习，你已经掌握了：

1. ✅ Python环境搭建与基础语法
2. ✅ 数据类型与变量操作
3. ✅ 控制流与函数设计
4. ✅ 面向对象编程基础
5. ✅ 文件操作与异常处理

**下一步建议：**

1. **深入学习**：继续学习Python高级特性，如装饰器、生成器、协程等
2. **实践项目**：通过实际项目巩固所学知识
3. **算法学习**：结合Python学习数据结构与算法
4. **框架学习**：学习Django、Flask等Web框架
5. **数据科学**：学习pandas、numpy、matplotlib等数据处理库

**🎉 学习成果：**

你现在具备了扎实的Python编程基础，可以：
- 独立开发小型应用程序
- 理解和编写面向对象代码
- 处理文件和数据操作
- 使用异常处理机制
- 编写模块化的可维护代码

继续加油，Python学习之旅才刚刚开始！

---

## 📚 分页导航

[← 第4期：面向对象编程基础](./lesson-04) [第5期：文件操作与异常处理](./lesson-05) →
