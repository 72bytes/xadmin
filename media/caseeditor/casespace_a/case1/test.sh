#!/bin/bash
# Monaco Editor Shell Script Test
# 测试 Shell 语法高亮和代码折叠

# 函数定义
function greet() {
    local name=$1
    echo "Hello, ${name}!"
}

# 变量定义
APP_NAME="Monaco Editor Test"
VERSION="1.0.0"

# 条件语句
if [ -f "/etc/passwd" ]; then
    echo "File exists"
else
    echo "File not found"
fi

# 循环语句
for i in {1..5}; do
    echo "Count: $i"
done

# 数组
declare -a fruits=("apple" "banana" "orange")
for fruit in "${fruits[@]}"; do
    echo "Fruit: $fruit"
done

# 调用函数
greet "World"

echo "Script completed successfully!"


