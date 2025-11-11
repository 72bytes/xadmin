#!/usr/bin/env python3
"""
Monaco Editor Python Test
测试 Python 语法高亮和代码折叠
"""

def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    """简单的计算器类"""
    
    def __init__(self):
        self.result = 0
    
    def add(self, x, y):
        """加法运算"""
        self.result = x + y
        return self.result
    
    def multiply(self, x, y):
        """乘法运算"""
        self.result = x * y
        return self.result

if __name__ == "__main__":
    # 测试 fibonacci
    print("Fibonacci(10):", fibonacci(10))
    
    # 测试 Calculator
    calc = Calculator()
    print("5 + 3 =", calc.add(5, 3))
    print("5 * 3 =", calc.multiply(5, 3))


