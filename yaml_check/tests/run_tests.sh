#!/bin/bash
# YAML Check 模块测试运行脚本

# 激活虚拟环境
source "$(dirname "$0")/../../.venv/bin/activate"

echo "========================================"
echo "YAML Check 模块测试"
echo "========================================"
echo ""

# 检查 pytest 是否安装
if ! python -c "import pytest" 2>/dev/null; then
    echo "❌ pytest 未安装，正在安装..."
    uv pip install pytest pytest-django pytest-cov
fi

# 运行测试
echo "🚀 开始运行测试..."
echo ""

# 根据参数决定运行方式
case "$1" in
    "quick")
        # 快速测试（跳过慢速测试）
        echo "📊 快速测试模式（跳过慢速测试）"
        pytest yaml_check/tests/ -v -m "not slow"
        ;;
    "cov")
        # 带覆盖率
        echo "📊 覆盖率测试模式"
        pytest yaml_check/tests/ -v --cov=yaml_check --cov-report=term-missing --cov-report=html
        echo ""
        echo "📄 HTML 覆盖率报告: htmlcov/index.html"
        ;;
    "fast")
        # 并行运行
        echo "⚡ 并行测试模式"
        pytest yaml_check/tests/ -v -n auto
        ;;
    "debug")
        # 调试模式
        echo "🐛 调试模式（显示详细输出）"
        pytest yaml_check/tests/ -v -s --showlocals
        ;;
    *)
        # 默认模式
        echo "📊 标准测试模式"
        pytest yaml_check/tests/ -v
        ;;
esac

echo ""
echo "========================================"
echo "测试完成"
echo "========================================"




