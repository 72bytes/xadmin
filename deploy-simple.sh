#!/bin/bash
# XAdmin Docker 简化部署脚本（使用外部数据库）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Docker Compose 命令检测
DOCKER_COMPOSE=""

detect_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    else
        print_error "Docker Compose 未找到，请安装 Docker Compose"
        exit 1
    fi
}

# 检查 Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    detect_docker_compose
    print_info "Docker 环境检查通过 (使用: $DOCKER_COMPOSE)"
}

# 构建镜像
build() {
    print_info "开始构建 Docker 镜像..."
    $DOCKER_COMPOSE -f docker-compose.simple.yml build --no-cache
    print_info "镜像构建完成"
}

# 启动服务
start() {
    print_info "启动服务..."
    $DOCKER_COMPOSE -f docker-compose.simple.yml up -d
    print_info "服务启动完成"
    print_info ""
    print_info "访问地址:"
    print_info "  前端: http://localhost"
    print_info "  后端: http://localhost:9527"
}

# 停止服务
stop() {
    print_info "停止服务..."
    $DOCKER_COMPOSE -f docker-compose.simple.yml down
    print_info "服务已停止"
}

# 查看日志
logs() {
    $DOCKER_COMPOSE -f docker-compose.simple.yml logs -f --tail=100 "${1:-}"
}

# 查看状态
status() {
    $DOCKER_COMPOSE -f docker-compose.simple.yml ps
}

# 重启
restart() {
    print_info "重启服务..."
    $DOCKER_COMPOSE -f docker-compose.simple.yml restart
    print_info "服务已重启"
}

# 进入容器
shell() {
    SERVICE="${1:-backend}"
    $DOCKER_COMPOSE -f docker-compose.simple.yml exec "$SERVICE" sh
}

# Django 命令
manage() {
    $DOCKER_COMPOSE -f docker-compose.simple.yml exec backend python manage.py "$@"
}

# 一键安装
install() {
    print_info "=========================================="
    print_info "   XAdmin Docker 一键部署"
    print_info "=========================================="
    print_info ""
    
    check_docker
    
    print_warn "注意：此部署使用您现有的外部数据库配置"
    print_warn "数据库地址: 10.67.167.53:5433"
    print_warn "请确保网络可以访问此数据库"
    print_info ""
    
    read -p "按 Enter 继续部署，或 Ctrl+C 取消..."
    
    build
    start
    
    sleep 5
    
    print_info ""
    print_info "=========================================="
    print_info "   部署完成！"
    print_info "=========================================="
    print_info ""
    print_info "访问地址:"
    print_info "  前端: http://服务器IP"
    print_info "  后端: http://服务器IP:9527"
    print_info ""
    print_info "常用命令:"
    print_info "  查看状态: ./deploy-simple.sh status"
    print_info "  查看日志: ./deploy-simple.sh logs"
    print_info "  重启服务: ./deploy-simple.sh restart"
    print_info "  停止服务: ./deploy-simple.sh stop"
    print_info ""
}

# 帮助信息
help() {
    cat << EOF
XAdmin Docker 简化部署脚本

用法: $0 [命令]

命令:
  install    一键安装并启动
  build      构建镜像
  start      启动服务
  stop       停止服务
  restart    重启服务
  status     查看状态
  logs       查看日志
  shell      进入后端容器
  manage     运行 Django 命令
  help       显示帮助

示例:
  $0 install              # 一键部署
  $0 logs backend         # 查看后端日志
  $0 manage migrate       # 运行迁移
  $0 shell                # 进入后端容器

EOF
}

# 主函数
case "${1:-help}" in
    install)
        install
        ;;
    build)
        check_docker
        build
        ;;
    start)
        check_docker
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    shell)
        shell "$2"
        ;;
    manage)
        shift
        manage "$@"
        ;;
    help|--help|-h)
        help
        ;;
    *)
        print_error "未知命令: $1"
        help
        exit 1
        ;;
esac

