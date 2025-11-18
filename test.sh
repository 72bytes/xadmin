#!/bin/bash
#
# 测试环境自动化部署脚本
# 用于在干净的 VM 测试机上快速搭建测试环境并执行测试
#
# 功能：
# 1. 自动安装 uv 包管理工具
# 2. 创建 Python 虚拟环境
# 3. 安装项目依赖
# 4. 执行 pytest 测试
# 5. 生成 HTML 和 XML 测试报告
#
# 使用方法：
#   chmod +x test.sh
#   ./test.sh
#

set -e  # 遇到错误立即退出
# set -x  # 取消注释以启用调试模式

# ============================================================================
# 环境变量预设（确保常用路径在 PATH 中）
# ============================================================================

# 添加常见的工具安装路径
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:$PATH"

# Source uv 环境文件（如果存在）
[ -f "$HOME/.local/bin/env" ] && source "$HOME/.local/bin/env" 2>/dev/null || true
[ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env" 2>/dev/null || true

# ============================================================================
# 颜色定义
# ============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# 辅助函数
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_separator() {
    echo "============================================================================"
}

# ============================================================================
# 主脚本开始
# ============================================================================

print_separator
log_info "开始测试环境部署..."
print_separator

# 记录开始时间
START_TIME=$(date +%s)

# ============================================================================
# 1. 环境检查
# ============================================================================

log_info "步骤 1/7: 检查系统环境..."

# 检查操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    log_info "操作系统: $NAME $VERSION"
else
    log_warning "无法检测操作系统版本"
fi

# 检查 Python 版本
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log_info "Python 版本: $PYTHON_VERSION"
else
    log_error "Python3 未安装，请先安装 Python 3.13 或更高版本"
    exit 1
fi

# 检查必要的系统工具
log_info "检查必要的系统工具..."
REQUIRED_TOOLS=("curl" "git")
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v $tool &> /dev/null; then
        log_warning "$tool 未安装，建议安装以获得更好的体验"
    fi
done

log_success "环境检查完成"

# ============================================================================
# 2. 安装 uv 包管理工具
# ============================================================================

log_info "步骤 2/7: 检查并安装 uv..."

if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    log_info "uv 已安装: $UV_VERSION"
else
    log_info "uv 未安装，正在安装..."
    
    # 安装 uv（使用官方安装脚本）
    if command -v curl &> /dev/null; then
        log_info "正在下载并安装 uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # 刷新环境变量 - 尝试多个可能的位置
        log_info "刷新环境变量..."
        
        # 常见的 uv 安装位置
        UV_PATHS=(
            "$HOME/.local/bin"
            "$HOME/.cargo/bin"
            "/usr/local/bin"
            "/root/.local/bin"
            "/root/.cargo/bin"
        )
        
        # 将所有可能的路径添加到 PATH
        for uv_path in "${UV_PATHS[@]}"; do
            if [ -d "$uv_path" ]; then
                export PATH="$uv_path:$PATH"
            fi
        done
        
        # Source 所有可能的环境文件
        [ -f "$HOME/.local/bin/env" ] && source "$HOME/.local/bin/env" 2>/dev/null || true
        [ -f "$HOME/.cargo/env" ] && source "$HOME/.cargo/env" 2>/dev/null || true
        [ -f "/root/.local/bin/env" ] && source "/root/.local/bin/env" 2>/dev/null || true
        
        # 等待一下，让系统刷新
        sleep 1
        
        # 多种方式验证 uv 是否可用
        UV_FOUND=false
        
        # 方法 1: 使用 command -v
        if command -v uv &> /dev/null; then
            UV_FOUND=true
            log_success "uv 安装成功: $(uv --version)"
        else
            # 方法 2: 尝试直接执行常见路径下的 uv
            for uv_path in "${UV_PATHS[@]}"; do
                if [ -x "$uv_path/uv" ]; then
                    UV_FOUND=true
                    # 创建软链接到 /usr/local/bin（如果有权限）
                    if [ -w "/usr/local/bin" ]; then
                        ln -sf "$uv_path/uv" /usr/local/bin/uv 2>/dev/null || true
                    fi
                    log_success "uv 安装成功: $($uv_path/uv --version)"
                    # 确保这个路径在 PATH 最前面
                    export PATH="$uv_path:$PATH"
                    break
                fi
            done
        fi
        
        # 最终验证
        if [ "$UV_FOUND" = false ]; then
            log_error "uv 安装后仍无法找到"
            log_info "安装脚本已执行，但 uv 不在标准路径中"
            log_info "请检查以下位置："
            for uv_path in "${UV_PATHS[@]}"; do
                echo "  - $uv_path"
            done
            log_info "或手动安装: pip3 install uv"
            exit 1
        fi
    else
        log_error "curl 未安装，无法自动安装 uv"
        log_info "请先安装 curl: apt-get install curl 或 yum install curl"
        log_info "或手动安装 uv: pip3 install uv"
        exit 1
    fi
fi

log_success "uv 准备就绪"

# ============================================================================
# 3. 创建虚拟环境
# ============================================================================

log_info "步骤 3/7: 创建/激活 Python 虚拟环境..."

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

log_info "项目目录: $PROJECT_ROOT"

# 虚拟环境目录
VENV_DIR="$PROJECT_ROOT/.venv"

# 如果虚拟环境已存在，询问是否重新创建
if [ -d "$VENV_DIR" ]; then
    log_warning "虚拟环境已存在: $VENV_DIR"
    log_info "将使用现有虚拟环境"
else
    log_info "创建新的虚拟环境..."
    uv venv "$VENV_DIR" --python 3.13
    log_success "虚拟环境创建成功"
fi

# 激活虚拟环境
log_info "激活虚拟环境..."
source "$VENV_DIR/bin/activate"
log_success "虚拟环境已激活: $VIRTUAL_ENV"

# ============================================================================
# 4. 安装项目依赖
# ============================================================================

log_info "步骤 4/7: 安装项目依赖..."

# Django 项目不需要以可编辑模式安装，只需要安装依赖
log_info "安装主依赖..."
if [ -f "pyproject.toml" ]; then
    # 直接安装 pyproject.toml 中的依赖，不使用 -e 选项
    uv pip install \
        captcha \
        django \
        django-cors-headers \
        django-currentuser \
        django-ninja \
        django-ninja-extra \
        django-ninja-jwt \
        django-redis \
        gunicorn \
        loguru \
        "psycopg[binary]" \
        pyjwt \
        redis
else
    log_error "pyproject.toml 不存在"
    exit 1
fi

log_info "安装开发依赖（测试相关）..."
uv pip install \
    pytest \
    pytest-django \
    pytest-cov \
    pytest-html \
    pytest-xdist \
    pytest-timeout \
    pytest-json-report \
    coverage[toml] \
    pyyaml

log_success "依赖安装完成"

# 显示已安装的关键包
log_info "已安装的关键包版本:"
python -c "import django; print(f'  - Django: {django.__version__}')" 2>/dev/null || log_warning "Django 导入失败"
python -c "import pytest; print(f'  - pytest: {pytest.__version__}')" 2>/dev/null || log_warning "pytest 导入失败"

# ============================================================================
# 5. 环境准备
# ============================================================================

log_info "步骤 5/7: 准备测试环境..."

# 创建必要的目录
log_info "创建必要的目录..."
mkdir -p logs
mkdir -p test-reports
mkdir -p htmlcov

# 检查 Django 配置
log_info "检查 Django 配置..."
python manage.py check --deploy || log_warning "Django 配置检查发现警告（可忽略）"

log_success "环境准备完成"

# ============================================================================
# 6. 执行 pytest 测试
# ============================================================================

log_info "步骤 6/7: 执行 pytest 测试..."

# 定义测试报告输出路径
HTML_REPORT="test-reports/pytest_report_$(date +%Y%m%d_%H%M%S).html"
XML_REPORT="test-reports/pytest_report_$(date +%Y%m%d_%H%M%S).xml"
JSON_REPORT="test-reports/pytest_report_$(date +%Y%m%d_%H%M%S).json"

log_info "HTML 报告: $HTML_REPORT"
log_info "XML 报告:  $XML_REPORT"
log_info "JSON 报告: $JSON_REPORT"

print_separator
log_info "开始执行测试..."
print_separator

# 执行 pytest，生成多种格式的报告
# 说明：
# - -v: 详细输出
# - --tb=short: 简短的错误回溯
# - --color=yes: 彩色输出
# - --html: 生成 HTML 报告
# - --junitxml: 生成 JUnit XML 报告（Jenkins/CI 兼容）
# - --json-report: 生成 JSON 报告
# - --cov: 代码覆盖率
# - --cov-report: 覆盖率报告格式
# - -n auto: 并行测试（可选，根据 CPU 核心数自动调整）

pytest \
    -v \
    --tb=short \
    --color=yes \
    --html="$HTML_REPORT" \
    --self-contained-html \
    --junitxml="$XML_REPORT" \
    --json-report \
    --json-report-file="$JSON_REPORT" \
    --cov=. \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    --cov-report=xml:test-reports/coverage.xml \
    --cov-config=.coveragerc \
    --durations=10 \
    --maxfail=5 \
    || TEST_EXIT_CODE=$?

# 保存测试退出码（0=全部通过，非0=有失败）
TEST_EXIT_CODE=${TEST_EXIT_CODE:-0}

print_separator
if [ $TEST_EXIT_CODE -eq 0 ]; then
    log_success "所有测试通过！"
else
    log_warning "部分测试失败（退出码: $TEST_EXIT_CODE）"
fi
print_separator

# ============================================================================
# 7. 生成测试报告摘要
# ============================================================================

log_info "步骤 7/7: 生成测试报告摘要..."

# 创建测试报告索引
SUMMARY_FILE="test-reports/TEST_SUMMARY.md"

cat > "$SUMMARY_FILE" << EOF
# 测试报告摘要

## 测试信息

- **测试时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **项目路径**: $PROJECT_ROOT
- **Python 版本**: $(python --version)
- **pytest 版本**: $(pytest --version)
- **测试结果**: $([ $TEST_EXIT_CODE -eq 0 ] && echo "✅ 全部通过" || echo "❌ 部分失败")

## 测试报告文件

- **HTML 报告**: [$HTML_REPORT]($HTML_REPORT)
- **XML 报告**: [$XML_REPORT]($XML_REPORT)
- **JSON 报告**: [$JSON_REPORT]($JSON_REPORT)
- **覆盖率报告**: [htmlcov/index.html](htmlcov/index.html)

## 快速查看报告

### 在浏览器中打开 HTML 报告

\`\`\`bash
# Linux
xdg-open $HTML_REPORT

# macOS
open $HTML_REPORT

# Windows (WSL)
explorer.exe $(wslpath -w $HTML_REPORT)
\`\`\`

### 查看覆盖率报告

\`\`\`bash
# Linux
xdg-open htmlcov/index.html

# macOS
open htmlcov/index.html

# Windows (WSL)
explorer.exe $(wslpath -w htmlcov/index.html)
\`\`\`

## 测试文件列表

EOF

# 添加测试文件列表
find tests -name "test_*.py" -o -name "*_test.py" | while read -r file; do
    echo "- \`$file\`" >> "$SUMMARY_FILE"
done

log_success "测试报告摘要已生成: $SUMMARY_FILE"

# ============================================================================
# 完成
# ============================================================================

# 计算总耗时
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

print_separator
log_success "测试流程完成！"
print_separator

echo ""
log_info "总耗时: ${MINUTES}分${SECONDS}秒"
echo ""
log_info "测试报告位置:"
echo "  📊 HTML 报告:  $HTML_REPORT"
echo "  📋 XML 报告:   $XML_REPORT"
echo "  📈 覆盖率报告: htmlcov/index.html"
echo "  📝 摘要文件:   $SUMMARY_FILE"
echo ""

# 显示如何查看报告
log_info "查看报告方法:"
echo "  🌐 浏览器查看: firefox $HTML_REPORT"
echo "  📁 文件管理器: cd test-reports && ls -lh"
echo ""

# 根据测试结果返回相应的退出码
# 注意：为了让 Jenkins 能够收集报告，即使测试失败也返回 0
if [ $TEST_EXIT_CODE -eq 0 ]; then
    log_success "🎉 所有测试通过！项目质量良好。"
else
    log_warning "⚠️  部分测试失败，请查看报告了解详情。"
fi

# 总是返回 0，让 Jenkins 继续收集报告
exit 0

