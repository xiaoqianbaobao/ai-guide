---
title: 控制流与函数
description: 学习Python的控制流结构和函数定义，掌握程序流程控制
---

# 第${i}期：控制流与函数

## 📖 学习目标

- 掌握条件语句（if-elif-else）的使用
- 熟练使用循环语句（for, while）
- 理解break与continue语句的作用
- 学会定义和调用函数
- 掌握参数传递与返回值机制
- 理解作用域与命名空间概念

## 🎯 条件语句（if-elif-else）

### if语句

```python
# 基本if语句
age = 18
if age >= 18:
    print("已成年")
    print("可以投票")

# if-else语句
score = 85
if score >= 60:
    print("及格")
else:
    print("不及格")

# if-elif-else语句
score = 85
if score >= 90:
    grade = "优秀"
elif score >= 80:
    grade = "良好"
elif score >= 70:
    grade = "中等"
elif score >= 60:
    grade = "及格"
else:
    grade = "不及格"

print(f"成绩等级: {grade}")
```

### 条件表达式（三元运算符）

```python
# 传统if-else
age = 18
if age >= 18:
    status = "成年"
else:
    status = "未成年"

# 条件表达式（推荐）
status = "成年" if age >= 18 else "未成年"

# 嵌套条件表达式
score = 85
result = "优秀" if score >= 90 else ("良好" if score >= 80 else "及格")

print(f"结果: {result}")
```

### 复合条件判断

```python
# and, or, not 运算符
age = 25
has_license = True
has_car = False

# and 运算符
if age >= 18 and has_license:
    print("可以开车")

# or 运算符
if has_license or has_car:
    print("有交通工具")

# not 运算符
if not has_car:
    print("没有车")

# 复合条件
if (age >= 18 and has_license) or has_car:
    print("可以独立出行")
```

## 🔄 循环语句

### for循环

```python
# 遍历列表
fruits = ["苹果", "香蕉", "橙子"]
for fruit in fruits:
    print(f"我喜欢吃{fruit}")

# 遍历字符串
for char in "Python":
    print(char)

# 使用range()函数
for i in range(5):
    print(f"第{i+1}次循环")

# range()的高级用法
print("步长为2:", list(range(0, 10, 2)))  # [0, 2, 4, 6, 8]
print("反向循环:", list(range(5, 0, -1)))  # [5, 4, 3, 2, 1]

# 嵌套for循环
for i in range(3):
    for j in range(2):
        print(f"({i}, {j})")
```

### while循环

```python
# 基本while循环
count = 0
while count < 5:
    print(f"计数: {count}")
    count += 1

# 无限循环 + break
import random
target = random.randint(1, 10)
guess = 0

while True:
    guess = int(input("猜一个数字(1-10): "))
    if guess == target:
        print("猜对了!")
        break
    elif guess < target:
        print("太小了")
    else:
        print("太大了")

# while-else结构
count = 0
while count < 3:
    print(f"尝试{count + 1}")
    count += 1
else:
    print("所有尝试完成")
```

### 循环控制语句

```python
# break语句
for i in range(10):
    if i == 5:
        break
    print(i)
# 输出: 0 1 2 3 4

# continue语句
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)
# 输出: 1 3 5 7 9

# pass语句（占位符）
for i in range(5):
    if i == 2:
        pass  # 占位，什么也不做
    else:
        print(i)
```

## 🎤 函数定义与调用

### 函数定义

```python
# 基本函数定义
def greet():
    """问候函数"""
    print("你好!")

# 无参数函数
def get_pi():
    return 3.14159

# 有参数函数
def add(a, b):
    """加法函数"""
    return a + b

# 多参数函数
def calculate(x, y, operation="add"):
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y
    else:
        return 0

# 调用函数
greet()
result = add(3, 5)
print(f"3 + 5 = {result}")
```

### 参数传递

```python
# 位置参数
def introduce(name, age):
    print(f"我叫{name}，今年{age}岁")

introduce("张三", 25)  # 位置匹配

# 关键字参数
introduce(age=30, name="李四")  # 键值匹配

# 默认参数
def greet(name, greeting="你好"):
    print(f"{greeting}，{name}!")

greet("王五")  # 使用默认问候
greet("赵六", "早上好")

# 可变参数 *args
def sum_all(*numbers):
    total = 0
    for num in numbers:
        total += num
    return total

print(sum_all(1, 2, 3, 4, 5))  # 15

# 关键字可变参数 **kwargs
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="张三", age=25, city="北京")
```

### 返回值

```python
# 单个返回值
def square(x):
    return x ** 2

result = square(5)
print(result)  # 25

# 多个返回值（返回元组）
def get_name_age():
    return "张三", 25

name, age = get_name_age()
print(f"姓名: {name}, 年龄: {age}")

# 返回None（默认）
def no_return():
    print("这个函数没有显式返回值")

result = no_return()
print(result)  # None
```

## 🌍 作用域与命名空间

### 作用域层次

```python
# 全局变量
global_var = "我是全局变量"

def outer_function():
    # 外部函数变量
    outer_var = "我是外部函数变量"
    
    def inner_function():
        # 内部函数变量
        inner_var = "我是内部函数变量"
        print(f"内部函数: {inner_var}")
        print(f"外部函数变量: {outer_var}")
        print(f"全局变量: {global_var}")
    
    inner_function()
    print(f"外部函数变量: {outer_var}")
    # print(inner_var)  # 错误！内部变量无法访问

outer_function()
print(f"全局变量: {global_var}")
# print(outer_var)  # 错误！外部变量无法访问
```

### global和nonlocal关键字

```python
# global关键字
counter = 0

def increment():
    global counter
    counter += 1
    return counter

print(increment())  # 1
print(increment())  # 2

# nonlocal关键字
def outer():
    x = 10
    
    def inner():
        nonlocal x
        x = 20
        print(f"内部函数中: {x}")
    
    print(f"外部函数中: {x}")
    inner()
    print(f"外部函数中(修改后): {x}")

outer()
```

## 🎓 练习题

### 基础练习

1. **条件判断**：编写程序判断输入的年份是否为闰年
2. **循环练习**：使用for循环打印九九乘法表
3. **函数定义**：实现一个简单的计算器，支持加减乘除

### 编程练习

1. **猜数字游戏**：编写一个猜数字游戏，统计用户猜测次数
2. **密码验证**：实现密码强度检查函数
3. **成绩统计**：编写程序统计学生成绩，计算平均分、最高分、最低分

### 挑战练习

1. **猜词游戏**：实现一个单词猜谜游戏
2. **计算器**：编写一个支持表达式计算的高级计算器
3. **数据处理**：实现一个简单的数据清洗和统计工具

## 🔗 扩展阅读

- [Python官方文档 - 条件表达式](https://docs.python.org/zh-cn/3/reference/expressions.html#conditional-expressions)
- [Python官方文档 - 循环语句](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#the-for-statement)
- [Python官方文档 - 函数定义](https://docs.python.org/zh-cn/3/reference/compound_stmts.html#function-definitions)
- [Python官方文档 - 命名空间](https://docs.python.org/zh-cn/3/tutorial/classes.html#python-scopes-and-namespaces)

---

**📝 本节小结：**

- 条件语句是程序流程控制的基础，支持复杂的判断逻辑
- 循环语句使程序能够重复执行，提高代码效率
- break和continue语句提供对循环执行的精细控制
- 函数是代码复用的基本单位，提高代码的模块化程度
- 作用域和命名空间定义了变量的可见范围和生命周期

**💡 下一节预告：** 在第4期中，我们将深入学习Python的面向对象编程，包括类的定义、对象的创建、继承与多态等核心概念。

---

## 📚 分页导航

[← 第2期：数据类型与变量](./lesson-02) [第4期：面向对象编程基础](./lesson-04) →
