#!/bin/bash
#
# 快速测试脚本（假设环境已经安装）
# 用于已经配置好环境的机器上快速运行测试
#
# 使用方法：
#   ./test-quick.sh [pytest参数]
#
# 示例：
#   ./test-quick.sh                    # 运行所有测试
#   ./test-quick.sh -m unit            # 只运行单元测试
#   ./test-quick.sh tests/test_*.py    # 只运行特定测试文件
#

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}快速测试模式${NC}"
echo -e "${BLUE}========================================${NC}"

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    echo -e "${GREEN}激活虚拟环境...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}虚拟环境不存在，请先运行 ./test.sh${NC}"
    exit 1
fi

# 创建报告目录
mkdir -p test-reports

# 生成报告文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
HTML_REPORT="test-reports/pytest_report_${TIMESTAMP}.html"
XML_REPORT="test-reports/pytest_report_${TIMESTAMP}.xml"

echo -e "${BLUE}开始运行测试...${NC}"
echo ""

# 运行 pytest，传递所有命令行参数
pytest \
    -v \
    --tb=short \
    --color=yes \
    --html="$HTML_REPORT" \
    --self-contained-html \
    --junitxml="$XML_REPORT" \
    --cov=. \
    --cov-report=html:htmlcov \
    --cov-report=term \
    --durations=5 \
    "$@" \
    || TEST_EXIT_CODE=$?

TEST_EXIT_CODE=${TEST_EXIT_CODE:-0}

echo ""
echo -e "${BLUE}========================================${NC}"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ 测试完成！${NC}"
else
    echo -e "${YELLOW}⚠️  部分测试失败${NC}"
fi
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "📊 HTML 报告: ${HTML_REPORT}"
echo -e "📋 XML 报告:  ${XML_REPORT}"
echo -e "📈 覆盖率:    htmlcov/index.html"
echo ""

exit $TEST_EXIT_CODE



