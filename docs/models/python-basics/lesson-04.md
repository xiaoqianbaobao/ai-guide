---
title: 面向对象编程基础
description: 学习Python的面向对象编程，掌握类与对象的概念
---

# 第4期：面向对象编程基础

## 📖 学习目标

- 理解面向对象编程的基本概念
- 掌握类与对象的定义和创建
- 学会属性与方法的操作
- 理解构造函数与析构函数的使用
- 掌握继承与多态的实现
- 理解封装性在Python中的应用

## 🏗️ 类与对象的概念

### 面向对象编程概述

面向对象编程（Object-Oriented Programming，OOP）是一种编程范式，它将现实世界中的事物抽象为对象，通过对象之间的交互来解决问题。

**核心概念：**
- **类（Class）**：对象的模板或蓝图
- **对象（Object）**：类的具体实例
- **属性（Attribute）**：对象的特征
- **方法（Method）**：对象的行为

### 类的定义

```python
# 基本类定义
class Person:
    """人类类"""
    
    # 类属性（所有实例共享）
    species = "人类"
    
    # 构造函数
    def __init__(self, name, age):
        # 实例属性
        self.name = name
        self.age = age
    
    # 实例方法
    def introduce(self):
        return f"我叫{self.name}，今年{self.age}岁"
    
    # 类方法
    @classmethod
    def get_species(cls):
        return cls.species
    
    # 静态方法
    @staticmethod
    def is_adult(age):
        return age >= 18

# 创建对象（实例化）
person1 = Person("张三", 25)
person2 = Person("李四", 16)

# 访问属性和方法
print(person1.name)           # 张三
print(person1.introduce())    # 我叫张三，今年25岁
print(Person.species)         # 人类
print(Person.get_species())   # 人类
print(Person.is_adult(20))    # True
```

## 📋 属性与方法

### 实例属性与类属性

```python
class Car:
    # 类属性
    wheels = 4
    manufacturer = "通用汽车"
    
    def __init__(self, brand, model, year):
        # 实例属性
        self.brand = brand
        self.model = model
        self.year = year
        self._mileage = 0  # 受保护的属性（约定）
        self.__engine_type = "V6"  # 私有属性
    
    # 实例方法
    def start(self):
        return f"{self.brand} {self.model} 启动了"
    
    def drive(self, miles):
        self._mileage += miles
        return f"行驶了{miles}英里"
    
    def get_info(self):
        return {
            "品牌": self.brand,
            "型号": self.model,
            "年份": self.year,
            "里程": self._mileage,
            "制造商": self.manufacturer,
            "轮子数": self.wheels
        }

# 创建汽车对象
car1 = Car("丰田", "凯美瑞", 2023)
car2 = Car("本田", "雅阁", 2022)

# 访问属性
print(car1.brand)             # 丰田
print(Car.wheels)             # 4
print(car1._mileage)          # 0
# print(car1.__engine_type)   # 错误！私有属性无法直接访问

# 调用方法
print(car1.start())           # 丰田 凯美瑞 启动了
print(car1.drive(50))         # 行驶了50英里
print(car1.get_info())
```

### 属性装饰器

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """获取摄氏度"""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """设置摄氏度"""
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """获取华氏度"""
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """设置华氏度"""
        self.celsius = (value - 32) * 5/9

# 使用属性装饰器
temp = Temperature(25)
print(f"摄氏度: {temp.celsius}")
print(f"华氏度: {temp.fahrenheit}")

temp.celsius = 30
print(f"摄氏度: {temp.celsius}")
print(f"华氏度: {temp.fahrenheit}")

temp.fahrenheit = 86
print(f"摄氏度: {temp.celsius}")
```

## 🏗️ 构造函数与析构函数

### 构造函数（__init__）

```python
class Student:
    # 类变量
    school_name = "Python大学"
    
    def __init__(self, name, student_id, major="计算机科学"):
        """构造函数：创建学生对象时自动调用"""
        self.name = name
        self.student_id = student_id
        self.major = major
        self.grades = []
        print(f"学生 {name} 已创建")
    
    def add_grade(self, grade):
        """添加成绩"""
        if 0 <= grade <= 100:
            self.grades.append(grade)
        else:
            raise ValueError("成绩必须在0-100之间")
    
    def get_average(self):
        """计算平均成绩"""
        if not self.grades:
            return 0
        return sum(self.grades) / len(self.grades)
    
    def __str__(self):
        """字符串表示"""
        return f"学生: {self.name}, 学号: {self.student_id}, 专业: {self.major}"
    
    def __repr__(self):
        """对象表示"""
        return f"Student('{self.name}', '{self.student_id}', '{self.major}')"

# 创建学生对象
student1 = Student("张三", "2023001")
student2 = Student("李四", "2023002", "数据科学")

print(student1)
print(student2)

# 添加成绩
student1.add_grade(85)
student1.add_grade(92)
student1.add_grade(78)

print(f"{student1.name} 的平均分: {student1.get_average():.2f}")
```

### 析构函数（__del__）

```python
import time

class DatabaseConnection:
    def __init__(self, connection_id):
        self.connection_id = connection_id
        self.is_connected = True
        print(f"数据库连接 {connection_id} 已建立")
    
    def query(self, sql):
        if self.is_connected:
            print(f"执行查询: {sql}")
            return f"查询结果来自连接{self.connection_id}"
        else:
            raise ConnectionError("数据库连接已断开")
    
    def close(self):
        """手动关闭连接"""
        self.is_connected = False
        print(f"数据库连接 {self.connection_id} 已关闭")
    
    def __del__(self):
        """析构函数：对象销毁时自动调用"""
        if self.is_connected:
            print(f"警告: 数据库连接 {self.connection_id} 未手动关闭，自动关闭")
            self.is_connected = False

# 使用数据库连接
db = DatabaseConnection("db_001")
result = db.query("SELECT * FROM users")
print(result)

# 手动关闭连接
db.close()

# 创建另一个连接
db2 = DatabaseConnection("db_002")
# 程序结束时，__del__方法会自动调用
```

## 🔄 继承与多态

### 单继承

```python
# 基类（父类）
class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def speak(self):
        return "动物发出声音"
    
    def move(self):
        return f"{self.name} 在移动"

# 派生类（子类）
class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)  # 调用父类构造函数
        self.breed = breed
    
    def speak(self):  # 重写父类方法
        return f"{self.name} 汪汪叫"
    
    def fetch(self):  # 子类特有方法
        return f"{self.name} 去捡球了"

class Cat(Animal):
    def __init__(self, name, age, color):
        super().__init__(name, age)
        self.color = color
    
    def speak(self):  # 重写父类方法
        return f"{self.name} 喵喵叫"
    
    def climb(self):  # 子类特有方法
        return f"{self.name} 爬到树上了"

# 使用继承
dog = Dog("旺财", 3, "金毛")
cat = Cat("咪咪", 2, "橘色")

print(dog.speak())  # 旺财 汪汪叫
print(cat.speak())  # 咪咪 喵喵叫
print(dog.fetch())  # 旺财 去捡球了
print(cat.climb())  # 咪咪 爬到树上了
```

### 多继承

```python
class Flyable:
    def __init__(self, max_altitude):
        self.max_altitude = max_altitude
    
    def fly(self):
        return f"飞行高度: {self.max_altitude}米"
    
    def land(self):
        return "安全着陆"

class Bird(Animal, Flyable):
    def __init__(self, name, age, species, max_altitude):
        Animal.__init__(self, name, age)  # 多继承时需要显式调用
        Flyable.__init__(self, max_altitude)
        self.species = species
    
    def speak(self):
        return f"{self.name} 啾啾叫"
    
    def move(self):
        return f"{self.name} 飞行中"

# 使用多继承
eagle = Bird("老鹰", 5, "猛禽", 3000)
print(eagle.speak())        # 老鹰 啾啾叫
print(eagle.fly())          # 飞行高度: 3000米
print(eagle.move())         # 老鹰 飞行中
```

### 多态

```python
def animal_speak(animal):
    """多态函数：接受任何Animal对象"""
    return animal.speak()

# 创建不同类型的动物
animals = [
    Dog("旺财", 3, "金毛"),
    Cat("咪咪", 2, "橘色"),
    Bird("小鸟", 1, "雀科", 100)
]

# 多态调用
for animal in animals:
    print(animal_speak(animal))

# isinstance() 检查对象类型
print(isinstance(dog, Dog))        # True
print(isinstance(dog, Animal))     # True
print(isinstance(cat, Dog))        # False
```

## 🔒 封装性

### 访问控制

```python
class BankAccount:
    def __init__(self, account_number, initial_balance=0):
        self.account_number = account_number
        self.__balance = initial_balance  # 私有属性
        self._transaction_history = []    # 受保护属性
    
    @property
    def balance(self):
        """只读属性：余额"""
        return self.__balance
    
    def deposit(self, amount):
        """存款"""
        if amount > 0:
            self.__balance += amount
            self._transaction_history.append(f"存款: +{amount}")
            return True
        return False
    
    def withdraw(self, amount):
        """取款"""
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            self._transaction_history.append(f"取款: -{amount}")
            return True
        return False
    
    def get_transaction_history(self):
        """获取交易记录"""
        return self._transaction_history.copy()

# 使用封装的银行账户
account = BankAccount("123456789", 1000)
print(f"初始余额: {account.balance}")

account.deposit(500)
print(f"存款后余额: {account.balance}")

account.withdraw(200)
print(f"取款后余额: {account.balance}")

# 尝试直接访问私有属性（会报错）
# print(account.__balance)  # AttributeError

# 通过方法访问
print("交易记录:", account.get_transaction_history())
```

### 特殊方法（魔术方法）

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        """字符串表示"""
        return f"Vector({self.x}, {self.y})"
    
    def __repr__(self):
        """对象表示"""
        return f"Vector({self.x}, {self.y})"
    
    def __add__(self, other):
        """+运算符"""
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        """-运算符"""
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        """*运算符"""
        return Vector(self.x * scalar, self.y * scalar)
    
    def __len__(self):
        """len()函数"""
        return 2
    
    def __getitem__(self, index):
        """索引访问"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Vector索引超出范围")

# 使用特殊方法
v1 = Vector(1, 2)
v2 = Vector(3, 4)

print(v1 + v2)  # Vector(4, 6)
print(v1 * 2)   # Vector(2, 4)
print(len(v1))  # 2
print(v1[0])    # 1
```

## 🎓 练习题

### 基础练习

1. **类的定义**：创建一个Rectangle类，包含长和宽属性，实现面积和周长计算方法
2. **继承练习**：创建一个Shape基类和Circle、Rectangle子类
3. **封装练习**：设计一个学生管理系统，使用封装保护数据

### 编程练习

1. **图形计算器**：实现一个支持多种图形计算的类系统
2. **员工管理系统**：创建员工类及其子类（全职、兼职、临时）
3. **图书管理系统**：设计图书和读者类，实现借阅功能

### 挑战练习

1. **设计模式**：实现单例模式、工厂模式等设计模式
2. **数据结构**：用面向对象方式实现链表、栈、队列等数据结构
3. **游戏开发**：创建一个简单的游戏类，包含角色、物品、场景等

## 🔗 扩展阅读

- [Python官方文档 - 类定义](https://docs.python.org/zh-cn/3/tutorial/classes.html)
- [Python官方文档 - 特殊方法名](https://docs.python.org/zh-cn/3/reference/datamodel.html#special-method-names)
- [Python官方文档 - 继承](https://docs.python.org/zh-cn/3/tutorial/classes.html#inheritance)
- [Python官方文档 - 多重继承](https://docs.python.org/zh-cn/3/tutorial/classes.html#multiple-inheritance)

---

**📝 本节小结：**

- 面向对象编程是现代编程的重要范式，提供了代码复用和模块化能力
- 类是对象的模板，对象是类的具体实例
- 属性定义对象的特征，方法定义对象的行为
- 构造函数和析构函数分别在对象创建和销毁时执行
- 继承允许创建具有父类特性的新类，多态使不同对象能以统一方式处理
- 封装通过访问控制保护数据，提高代码安全性

**💡 下一节预告：** 在第5期中，我们将学习Python的文件操作、异常处理、模块与包等高级主题，为实际项目开发打下坚实基础。