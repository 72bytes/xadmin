# 后端 Dockerfile
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制项目依赖文件
COPY pyproject.toml uv.lock ./

# 安装 uv 包管理器
RUN pip install uv

# 安装 Python 依赖
RUN uv pip install --system -r pyproject.toml

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p logs media/caseeditor

# 收集静态文件
RUN python manage.py collectstatic --noinput || true

# 暴露端口
EXPOSE 9527

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9527/system/health-check/')" || exit 1

# 启动命令
CMD ["gunicorn", "xadmin.wsgi:application", "-c", "gunicorn.conf.py"]







