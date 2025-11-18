#!/bin/bash
# 路由测试快速运行脚本
# 用法: ./run_route_tests.sh [选项]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="/home/zx/xadmin_zx"
cd "$PROJECT_DIR"

# 激活虚拟环境
echo -e "${BLUE}激活虚拟环境...${NC}"
source .venv/bin/activate

# 显示帮助信息
show_help() {
    echo -e "${GREEN}路由测试快速运行脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  all          - 运行所有路由测试（默认）"
    echo "  reg          - 只运行路由注册检查（快速）"
    echo "  func         - 只运行路由功能测试"
    echo "  yaml         - 只测试YAML相关路由"
    echo "  auth         - 只测试认证相关路由"
    echo "  batch        - 批量检查所有路由"
    echo "  conflict     - 检查路由冲突"
    echo "  verbose      - 详细输出模式"
    echo "  help         - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 reg       # 快速检查路由注册"
    echo "  $0 yaml      # 测试YAML路由"
    echo "  $0 all       # 运行所有测试"
}

# 运行测试并显示结果
run_test() {
    local test_name=$1
    local test_cmd=$2
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}运行: $test_name${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if $test_cmd; then
        echo -e "${GREEN}✅ $test_name 通过${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name 失败${NC}"
        return 1
    fi
}

# 解析命令行参数
case "${1:-all}" in
    help|-h|--help)
        show_help
        exit 0
        ;;
    
    reg|registration)
        echo -e "${YELLOW}🔍 快速检查路由注册状态...${NC}"
        run_test "路由注册检查" "pytest tests/test_route_registration.py::TestRouteRegistration -v --tb=line"
        ;;
    
    batch)
        echo -e "${YELLOW}🔍 批量检查所有路由...${NC}"
        run_test "批量路由检查" "pytest tests/test_route_registration.py::TestBatchRouteCheck -v"
        ;;
    
    func|function)
        echo -e "${YELLOW}🧪 运行路由功能测试...${NC}"
        run_test "路由功能测试" "pytest tests/test_routes.py -v --tb=short"
        ;;
    
    yaml)
        echo -e "${YELLOW}🔍 测试YAML相关路由...${NC}"
        echo ""
        run_test "YAML路由注册" "pytest tests/test_route_registration.py::TestRouteRegistration::test_yaml_validate_route_registered -v"
        run_test "YAML路由功能" "pytest tests/test_routes.py::TestYamlCheckRoutes -v --tb=short"
        ;;
    
    auth)
        echo -e "${YELLOW}🔐 测试认证相关路由...${NC}"
        run_test "认证路由测试" "pytest tests/test_routes.py::TestAuthRoutes -v --tb=short"
        ;;
    
    conflict)
        echo -e "${YELLOW}⚠️  检查路由冲突...${NC}"
        run_test "路由冲突检查" "pytest tests/test_route_registration.py::TestRouteConflicts -v"
        ;;
    
    verbose|-v)
        echo -e "${YELLOW}📊 运行所有测试（详细模式）...${NC}"
        pytest tests/test_route_registration.py tests/test_routes.py -v --tb=short
        ;;
    
    all)
        echo -e "${YELLOW}🚀 运行完整路由测试套件...${NC}"
        
        # 1. 路由注册检查
        run_test "路由注册检查" "pytest tests/test_route_registration.py::TestRouteRegistration -v --tb=line"
        reg_result=$?
        
        # 2. 批量路由检查
        run_test "批量路由检查" "pytest tests/test_route_registration.py::TestBatchRouteCheck -v --tb=line"
        batch_result=$?
        
        # 3. 路由冲突检查
        run_test "路由冲突检查" "pytest tests/test_route_registration.py::TestRouteConflicts -v --tb=line"
        conflict_result=$?
        
        # 4. 路由功能测试
        run_test "路由功能测试" "pytest tests/test_routes.py -v --tb=line"
        func_result=$?
        
        # 汇总结果
        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}测试汇总${NC}"
        echo -e "${BLUE}========================================${NC}"
        
        [ $reg_result -eq 0 ] && echo -e "${GREEN}✅ 路由注册检查通过${NC}" || echo -e "${RED}❌ 路由注册检查失败${NC}"
        [ $batch_result -eq 0 ] && echo -e "${GREEN}✅ 批量路由检查通过${NC}" || echo -e "${RED}❌ 批量路由检查失败${NC}"
        [ $conflict_result -eq 0 ] && echo -e "${GREEN}✅ 路由冲突检查通过${NC}" || echo -e "${RED}❌ 路由冲突检查失败${NC}"
        [ $func_result -eq 0 ] && echo -e "${GREEN}✅ 路由功能测试通过${NC}" || echo -e "${RED}❌ 路由功能测试失败${NC}"
        
        # 如果所有测试都通过
        if [ $reg_result -eq 0 ] && [ $batch_result -eq 0 ] && [ $conflict_result -eq 0 ] && [ $func_result -eq 0 ]; then
            echo ""
            echo -e "${GREEN}🎉 所有路由测试通过！${NC}"
            exit 0
        else
            echo ""
            echo -e "${RED}❌ 部分测试失败，请查看上述输出${NC}"
            exit 1
        fi
        ;;
    
    *)
        echo -e "${RED}❌ 未知选项: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ 测试完成${NC}"


