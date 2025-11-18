#!/bin/bash
# XAdmin Docker 部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    print_info "Docker 环境检查通过"
}

# 检查环境变量文件
check_env() {
    if [ ! -f .env ]; then
        print_warn ".env 文件不存在，从 .env.example 复制"
        cp .env.example .env
        print_warn "请编辑 .env 文件，配置必要的环境变量"
        read -p "是否现在编辑 .env 文件？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    fi
    print_info "环境变量文件检查完成"
}

# 构建镜像
build_images() {
    print_info "开始构建 Docker 镜像..."
    docker-compose build --no-cache
    print_info "镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动服务..."
    docker-compose up -d
    print_info "服务启动完成"
}

# 停止服务
stop_services() {
    print_info "停止服务..."
    docker-compose down
    print_info "服务已停止"
}

# 查看日志
view_logs() {
    docker-compose logs -f --tail=100 "${1:-}"
}

# 重启服务
restart_services() {
    print_info "重启服务..."
    docker-compose restart
    print_info "服务已重启"
}

# 清理所有数据
clean_all() {
    print_warn "警告：此操作将删除所有容器、卷和数据！"
    read -p "确认继续？(yes/no) " -r
    if [[ $REPLY == "yes" ]]; then
        print_info "清理所有数据..."
        docker-compose down -v
        print_info "清理完成"
    else
        print_info "操作已取消"
    fi
}

# 数据库备份
backup_db() {
    print_info "备份数据库..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose exec -T postgres pg_dump -U amd xadmin > "$BACKUP_FILE"
    print_info "数据库已备份到: $BACKUP_FILE"
}

# 数据库恢复
restore_db() {
    if [ -z "$1" ]; then
        print_error "请指定备份文件"
        exit 1
    fi
    
    print_warn "警告：此操作将覆盖现有数据库！"
    read -p "确认继续？(yes/no) " -r
    if [[ $REPLY == "yes" ]]; then
        print_info "恢复数据库..."
        docker-compose exec -T postgres psql -U amd xadmin < "$1"
        print_info "数据库恢复完成"
    else
        print_info "操作已取消"
    fi
}

# 进入容器
enter_container() {
    SERVICE="${1:-backend}"
    print_info "进入 $SERVICE 容器..."
    docker-compose exec "$SERVICE" sh
}

# 查看服务状态
check_status() {
    print_info "服务状态："
    docker-compose ps
}

# 运行 Django 命令
run_django_cmd() {
    if [ -z "$1" ]; then
        print_error "请指定 Django 命令"
        exit 1
    fi
    docker-compose exec backend python manage.py "$@"
}

# 创建超级用户
create_superuser() {
    print_info "创建 Django 超级用户..."
    docker-compose exec backend python manage.py createsuperuser
}

# 显示帮助信息
show_help() {
    cat << EOF
XAdmin Docker 部署脚本

用法: $0 [命令] [选项]

命令:
  install         首次安装（检查环境、构建镜像、启动服务）
  build           构建 Docker 镜像
  start           启动所有服务
  stop            停止所有服务
  restart         重启所有服务
  status          查看服务状态
  logs [服务名]    查看日志（默认所有服务）
  clean           清理所有数据（危险操作）
  
  backup          备份数据库
  restore <文件>   恢复数据库
  
  shell [服务名]   进入容器（默认 backend）
  manage <命令>    运行 Django 管理命令
  superuser       创建超级用户
  
  help            显示此帮助信息

示例:
  $0 install                      # 首次安装
  $0 start                        # 启动服务
  $0 logs backend                 # 查看后端日志
  $0 manage migrate              # 运行数据库迁移
  $0 backup                       # 备份数据库
  $0 restore backup_20231215.sql # 恢复数据库

EOF
}

# 首次安装
install() {
    print_info "开始安装 XAdmin..."
    check_docker
    check_env
    build_images
    start_services
    
    print_info "等待服务启动..."
    sleep 10
    
    print_info "运行数据库迁移..."
    run_django_cmd migrate
    
    print_info "创建超级用户..."
    create_superuser
    
    print_info "安装完成！"
    print_info "访问地址: http://localhost"
}

# 主函数
main() {
    case "${1:-help}" in
        install)
            install
            ;;
        build)
            check_docker
            build_images
            ;;
        start)
            check_docker
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            check_status
            ;;
        logs)
            view_logs "$2"
            ;;
        clean)
            clean_all
            ;;
        backup)
            backup_db
            ;;
        restore)
            restore_db "$2"
            ;;
        shell)
            enter_container "$2"
            ;;
        manage)
            shift
            run_django_cmd "$@"
            ;;
        superuser)
            create_superuser
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"

