---
title: 数据类型与变量
description: 深入学习Python的数据类型系统，包括数值、字符串、容器等核心概念
---

# 第2期：数据类型与变量

## 📖 学习目标

- 掌握Python的数值类型（int, float, complex）
- 熟练使用字符串的各种操作与格式化方法
- 理解并掌握列表、元组、字典、集合的特性和使用
- 学会类型转换与类型检查技巧
- 掌握Python的常用内置函数

## 📊 数值类型详解

### 整数（int）

Python中的整数可以是任意大小的，没有固定范围限制。

```python
# 基本整数操作
a = 42
b = -17
c = 0

# 大整数
big_num = 123456789012345678901234567890

# 进制表示
binary = 0b1010      # 二进制: 10
octal = 0o755        # 八进制: 493
hexadecimal = 0xFF   # 十六进制: 255

print(f"十进制: {a}, 二进制: {binary}, 八进制: {octal}, 十六进制: {hexadecimal}")
```

### 浮点数（float）

浮点数用于表示实数，使用IEEE 754双精度浮点格式。

```python
# 基本浮点数
pi = 3.14159
e = 2.71828

# 科学计数法
scientific = 1.5e-3      # 0.0015
scientific2 = 2.5e4      # 25000.0

# 特殊值
infinity = float('inf')   # 正无穷
negative_infinity = float('-inf')  # 负无穷
nan = float('nan')        # 非数值

print(f"π = {pi:.4f}")
print(f"科学计数法: {scientific}")
print(f"无穷大: {infinity}")
```

### 复数（complex）

复数由实部和虚部组成，虚部以j结尾。

```python
# 复数创建
z1 = 3 + 4j
z2 = complex(1, 2)  # 1 + 2j
z3 = 5j             # 0 + 5j

# 复数运算
print(f"z1 = {z1}")
print(f"z2 = {z2}")
print(f"z1 + z2 = {z1 + z2}")

# 复数属性
print(f"z1的实部: {z1.real}")
print(f"z1的虚部: {z1.imag}")
print(f"z1的模: {abs(z1)}")
```

## 📝 字符串操作与格式化

### 字符串创建与基本操作

```python
# 字符串创建
str1 = '单引号字符串'
str2 = "双引号字符串"
str3 = """三引号字符串
可以跨越多行"""

# 字符串连接
first_name = "张"
last_name = "三"
full_name = first_name + last_name

# 字符串重复
pattern = "Python "
repeated = pattern * 3

print(f"全名: {full_name}")
print(f"重复: {repeated}")
```

### 字符串格式化

#### 方法一：使用 % 格式化

```python
name = "张三"
age = 25
height = 1.75

# 基本格式化
message1 = "姓名: %s, 年龄: %d, 身高: %.2f" % (name, age, height)
print(message1)

# 格式化符号
# %s: 字符串
# %d: 整数
# %f: 浮点数
# %x: 十六进制
# %%: 百分号
```

#### 方法二：使用 format() 方法

```python
# 位置参数
message2 = "姓名: {}, 年龄: {}, 身高: {:.2f}".format(name, age, height)
print(message2)

# 命名参数
message3 = "姓名: {name}, 年龄: {age}, 身高: {height:.2f}".format(
    name=name, age=age, height=height
)
print(message3)

# 索引参数
message4 = "姓名: {0}, 年龄: {1}, 身高: {2:.2f}".format(name, age, height)
print(message4)
```

#### 方法三：使用 f-string（推荐）

```python
# f-string 格式化（Python 3.6+）
message5 = f"姓名: {name}, 年龄: {age}, 身高: {height:.2f}"
print(message5)

# 表达式计算
print(f"年龄明年将是: {age + 1}")

# 函数调用
print(f"姓名长度: {len(name)}")
```

### 字符串常用方法

```python
text = "  Hello, Python!  "

# 大小写转换
print(text.upper())           # HELLO, PYTHON!
print(text.lower())           # hello, python!
print(text.capitalize())      # Hello, python!
print(text.title())           # Hello, Python!

# 去除空白
print(text.strip())           # Hello, Python!
print(text.lstrip())          # Hello, Python!
print(text.rstrip())          #   Hello, Python!

# 查找与替换
print(text.find("Python"))    # 7
print(text.replace("Python", "World"))  #   Hello, World!

# 分割与连接
words = text.split()
print(words)                  # ['Hello,', 'Python!']
joined = "-".join(words)
print(joined)                 # Hello,-Python!

# 判断方法
print(text.startswith("  "))  # True
print(text.endswith("!  "))   # True
print("Python".isalpha())     # True
print("123".isdigit())        # True
```

## 📦 容器类型详解

### 列表（list）

列表是有序的可变序列，可以包含不同类型的元素。

```python
# 创建列表
fruits = ["苹果", "香蕉", "橙子"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "Python", 3.14, True]

# 访问元素
print(fruits[0])              # 苹果
print(fruits[-1])             # 橙子
print(fruits[1:3])            # ['香蕉', '橙子']

# 修改列表
fruits[0] = "葡萄"
fruits.append("西瓜")         # 添加元素
fruits.insert(1, "草莓")      # 插入元素
fruits.remove("香蕉")         # 删除元素
popped = fruits.pop()         # 弹出元素

# 列表操作
print(len(fruits))            # 列表长度
print(max(numbers))           # 最大值
print(min(numbers))           # 最小值
print(sum(numbers))           # 求和
```

### 元组（tuple）

元组是有序的不可变序列，创建后无法修改。

```python
# 创建元组
coordinates = (10, 20)
single_tuple = (42,)          # 单元素元组需要逗号
empty_tuple = ()

# 访问元素
print(coordinates[0])         # 10
print(coordinates[-1])        # 20

# 元组操作
print(len(coordinates))       # 2
print(coordinates + (30, 40)) # (10, 20, 30, 40)

# 元组解包
x, y = coordinates
print(f"x = {x}, y = {y}")

# 元组不可变性
# coordinates[0] = 15  # 错误！元组不可修改
```

### 字典（dict）

字典是无序的键值对集合，键必须是不可变类型。

```python
# 创建字典
person = {
    "name": "张三",
    "age": 25,
    "skills": ["Python", "JavaScript"],
    "address": {
        "city": "北京",
        "district": "朝阳区"
    }
}

# 访问和修改
print(person["name"])         # 张三
person["age"] = 26            # 修改值
person["email"] = "zhangsan@example.com"  # 添加新键值对

# 字典方法
print(person.keys())          # 所有键
print(person.values())        # 所有值
print(person.items())         # 键值对
print(person.get("name"))     # 安全获取
print(person.pop("email"))    # 弹出键值对

# 字典遍历
for key, value in person.items():
    print(f"{key}: {value}")
```

### 集合（set）

集合是无序的不重复元素序列。

```python
# 创建集合
unique_numbers = {1, 2, 3, 4, 5}
empty_set = set()             # 空集合

# 集合操作
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

# 并集
union = set1 | set2           # {1, 2, 3, 4, 5, 6}
union2 = set1.union(set2)

# 交集
intersection = set1 & set2    # {3, 4}
intersection2 = set1.intersection(set2)

# 差集
difference = set1 - set2      # {1, 2}
difference2 = set1.difference(set2)

# 对称差集
symmetric_diff = set1 ^ set2  # {1, 2, 5, 6}
symmetric_diff2 = set1.symmetric_difference(set2)

# 集合方法
unique_numbers.add(6)
unique_numbers.remove(2)      # 不存在会报错
unique_numbers.discard(2)     # 不存在不会报错
print(len(unique_numbers))
```

## 🔀 类型转换与类型检查

### 类型转换

```python
# 显式类型转换
str_num = "123"
int_num = int(str_num)        # 字符串转整数
float_num = float(str_num)    # 字符串转浮点数
str_list = str([1, 2, 3])     # 列表转字符串

# 数值类型转换
pi = 3.14159
int_pi = int(pi)              # 3
str_pi = str(pi)              # "3.14159"

# 容器类型转换
str_list = list("Python")     # ['P', 'y', 't', 'h', 'o', 'n']
tuple_list = tuple([1, 2, 3]) # (1, 2, 3)
set_list = set([1, 2, 2, 3])  # {1, 2, 3}
dict_list = dict([('a', 1), ('b', 2)])  # {'a': 1, 'b': 2}
```

### 类型检查

```python
# isinstance() 函数
value = 42
print(isinstance(value, int))        # True
print(isinstance(value, float))      # False
print(isinstance(value, (int, float))) # True

# type() 函数
print(type(value) == int)            # True
print(type(value) is int)            # True

# 特殊类型检查
print(type(None) is type(None))      # NoneType
print(type(lambda x: x) is type(lambda x: x))  # function
```

## 🛠️ 常用内置函数

### 数值函数

```python
# 绝对值
print(abs(-5))                    # 5
print(abs(-3.14))                 # 3.14

# 最大值/最小值
print(max(1, 5, 3, 9, 2))         # 9
print(min(1, 5, 3, 9, 2))         # 1

# 四舍五入
print(round(3.14159, 2))          # 3.14
print(round(3.14159))             # 3

# 幂运算
print(pow(2, 3))                  # 8
print(pow(2, 3, 5))               # 3 (2^3 % 5)
```

### 序列函数

```python
# 长度
print(len("Python"))              # 6
print(len([1, 2, 3, 4, 5]))       # 5
print(len({"a": 1, "b": 2}))      # 2

# 排序
numbers = [3, 1, 4, 1, 5]
sorted_numbers = sorted(numbers)  # [1, 1, 3, 4, 5]
numbers.sort()                    # 原地排序

# 反转
reversed_list = list(reversed([1, 2, 3, 4, 5]))  # [5, 4, 3, 2, 1]
```

### 映射函数

```python
# enumerate() - 枚举
fruits = ["苹果", "香蕉", "橙子"]
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# zip() - 打包
names = ["张三", "李四", "王五"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name}今年{age}岁")

# map() - 映射
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))  # [1, 4, 9, 16, 25]

# filter() - 过滤
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]
```

## 🎓 练习题

### 基础练习

1. **字符串格式化**：使用三种不同的方法格式化个人信息
2. **列表操作**：创建一个包含10个随机数的列表，实现排序、求和等操作
3. **字典应用**：创建一个学生成绩字典，实现成绩查询、统计等功能

### 编程练习

1. **学生成绩管理**：编写程序管理学生成绩，支持添加、删除、查询、统计功能
2. **购物车系统**：实现一个简单的购物车程序，支持添加商品、计算总价、优惠折扣
3. **电话簿**：创建一个电话簿程序，支持添加联系人、搜索、删除功能

### 挑战练习

1. **数据可视化**：使用列表和字典创建一个简单的数据统计程序
2. **文本分析**：编写程序分析文本内容，统计词频、句子数等
3. **迷宫求解**：使用列表实现迷宫数据结构，编写路径搜索算法

## 🔗 扩展阅读

- [Python官方文档 - 数字类型](https://docs.python.org/zh-cn/3/library/stdtypes.html#typesnumeric)
- [Python官方文档 - 序列类型](https://docs.python.org/zh-cn/3/library/stdtypes.html#sequence-types-list-tuple-range)
- [Python官方文档 - 映射类型](https://docs.python.org/zh-cn/3/library/stdtypes.html#mapping-types-dict)
- [Python官方文档 - 集合类型](https://docs.python.org/zh-cn/3/library/stdtypes.html#set-types-set-frozenset)

---

**📝 本节小结：**

- Python提供了丰富的数值类型，包括整数、浮点数和复数
- 字符串是不可变序列，支持多种格式化方法
- 列表、元组、字典、集合是Python的四大容器类型，各有特点
- 类型转换和类型检查是编程中的重要技能
- 掌握常用内置函数可以提高编程效率

**💡 下一节预告：** 在第4期中，我们将学习Python的控制流结构，包括条件语句和循环语句，以及函数的定义与使用。

---

## 📚 分页导航

[← 第1期：Python环境搭建与基础语法](./lesson-01) [第3期：控制流与函数](./lesson-03) →
