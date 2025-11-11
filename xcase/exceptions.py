"""
自定义异常类
"""


class XCaseException(Exception):
    """XCase 模块基础异常类"""
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class CaseNotFoundException(XCaseException):
    """Case 不存在异常"""
    def __init__(self, casespace: str, case_name: str):
        message = f"Case '{case_name}' not found in casespace '{casespace}'"
        super().__init__(message, code=404)
        self.casespace = casespace
        self.case_name = case_name


class CasespaceNotFoundException(XCaseException):
    """Casespace 不存在异常"""
    def __init__(self, casespace: str):
        message = f"Casespace '{casespace}' not found"
        super().__init__(message, code=404)
        self.casespace = casespace


class InvalidCaseNameException(XCaseException):
    """无效的 Case 名称异常"""
    def __init__(self, case_name: str, reason: str = ""):
        message = f"Invalid case name: '{case_name}'"
        if reason:
            message += f" - {reason}"
        super().__init__(message, code=400)
        self.case_name = case_name


class FileOperationException(XCaseException):
    """文件操作异常"""
    def __init__(self, operation: str, path: str, reason: str = ""):
        message = f"File operation '{operation}' failed for path '{path}'"
        if reason:
            message += f" - {reason}"
        super().__init__(message, code=500)
        self.operation = operation
        self.path = path


class PathTraversalException(XCaseException):
    """路径遍历攻击异常"""
    def __init__(self, path: str):
        message = f"Path traversal attempt detected: '{path}'"
        super().__init__(message, code=403)
        self.path = path


class InvalidFileTypeException(XCaseException):
    """无效的文件类型异常"""
    def __init__(self, filename: str, allowed_types: list = None):
        message = f"Invalid file type: '{filename}'"
        if allowed_types:
            message += f". Allowed types: {', '.join(allowed_types)}"
        super().__init__(message, code=400)
        self.filename = filename


class FileSizeLimitException(XCaseException):
    """文件大小超限异常"""
    def __init__(self, filename: str, size: int, max_size: int):
        message = f"File '{filename}' size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        super().__init__(message, code=413)
        self.filename = filename
        self.size = size
        self.max_size = max_size


class ArchiveExtractionException(XCaseException):
    """压缩包解压异常"""
    def __init__(self, filename: str, reason: str = ""):
        message = f"Failed to extract archive '{filename}'"
        if reason:
            message += f" - {reason}"
        super().__init__(message, code=500)
        self.filename = filename


class DuplicateCaseException(XCaseException):
    """Case 已存在异常"""
    def __init__(self, casespace: str, case_name: str):
        message = f"Case '{case_name}' already exists in casespace '{casespace}'"
        super().__init__(message, code=409)
        self.casespace = casespace
        self.case_name = case_name

