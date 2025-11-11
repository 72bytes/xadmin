"""
常量定义模块
"""

# 存储根目录名称
STORAGE_ROOT_NAME = "caseeditor"

# 默认编码
DEFAULT_ENCODING = 'utf-8'

# 备用编码（用于二进制类文件）
FALLBACK_ENCODING = 'latin-1'

# 支持的压缩包格式
SUPPORTED_ARCHIVE_FORMATS = ['.tar.gz', '.tgz', '.zip']

# 文件扩展名到编程语言的映射
LANGUAGE_EXTENSION_MAP = {
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.py': 'python',
    '.sh': 'shell',
    '.bash': 'shell',
    '.zsh': 'shell',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'javascript',
    '.tsx': 'typescript',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.less': 'less',
    '.xml': 'xml',
    '.sql': 'sql',
    '.md': 'markdown',
    '.txt': 'text',
    '.log': 'text',
    '.conf': 'text',
    '.ini': 'ini',
    '.toml': 'toml',
    '.go': 'go',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
}

# 文件上传大小限制（字节）
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# 压缩包上传大小限制（字节）
MAX_ARCHIVE_SIZE = 500 * 1024 * 1024  # 500MB

# 允许的文件类型（白名单）
ALLOWED_FILE_EXTENSIONS = [
    # 文本文件
    '.txt', '.md', '.log', '.conf', '.ini', '.toml',
    # 代码文件
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.c', '.cpp', '.h', '.hpp',
    '.rs', '.rb', '.php', '.sh', '.bash', '.zsh',
    # 配置文件
    '.json', '.yaml', '.yml', '.xml', '.env',
    # Web 文件
    '.html', '.css', '.scss', '.less',
    # 数据库
    '.sql',
    # 其他
    '.csv', '.tsv',
]

# 禁止的文件名模式（安全考虑）
FORBIDDEN_FILE_PATTERNS = [
    '..',  # 路径遍历
    '~',   # 备份文件
]

# 日志格式
LOG_FORMAT = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}'

