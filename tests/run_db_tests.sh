#!/bin/bash

# 数据库连接测试运行脚本

# 激活虚拟环境
source ../.venv/bin/activate

echo "========================================="
echo "  数据库连接测试"
echo "========================================="
echo ""

# 根据参数选择测试类型
case "$1" in
  "config")
    echo "🔍 测试数据库配置..."
    pytest test_database_connection.py::TestDatabaseConnection -v --tb=short
    ;;
  "default")
    echo "🔍 测试 default 数据库连接..."
    pytest test_database_connection.py::TestDefaultDatabaseConnection -v --tb=short
    ;;
  "tpdb")
    echo "🔍 测试 tpdb 数据库连接..."
    pytest test_database_connection.py::TestTpdbDatabaseConnection -v --tb=short
    ;;
  "ops")
    echo "🔍 测试数据库读写操作..."
    pytest test_database_connection.py::TestDatabaseOperations -v --tb=short
    ;;
  "health")
    echo "🔍 测试数据库健康状态..."
    pytest test_database_connection.py::TestDatabaseHealth -v --tb=short
    ;;
  "stats")
    echo "🔍 测试数据库统计信息..."
    pytest test_database_connection.py::TestDatabaseStats -v --tb=short
    ;;
  "all"|"")
    echo "🔍 运行所有数据库测试..."
    pytest test_database_connection.py -v --tb=short
    ;;
  "help")
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  config   - 测试数据库配置"
    echo "  default  - 测试 default 数据库"
    echo "  tpdb     - 测试 tpdb 数据库"
    echo "  ops      - 测试读写操作"
    echo "  health   - 测试健康状态"
    echo "  stats    - 测试统计信息"
    echo "  all      - 运行所有测试（默认）"
    echo "  help     - 显示帮助信息"
    ;;
  *)
    echo "❌ 未知选项: $1"
    echo "使用 '$0 help' 查看帮助"
    exit 1
    ;;
esac


