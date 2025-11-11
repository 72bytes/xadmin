"""
文件系统管理器

提供用例文件的增删改查、上传下载、压缩解压等功能。
"""
import os
import shutil
import tarfile
import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from django.conf import settings
from loguru import logger

from .constants import (
    STORAGE_ROOT_NAME,
    DEFAULT_ENCODING,
    FALLBACK_ENCODING,
    LANGUAGE_EXTENSION_MAP,
    SUPPORTED_ARCHIVE_FORMATS,
    FORBIDDEN_FILE_PATTERNS,
)
from .exceptions import (
    PathTraversalException,
    CaseNotFoundException,
    CasespaceNotFoundException,
    InvalidCaseNameException,
    FileOperationException,
    ArchiveExtractionException,
    DuplicateCaseException,
)


class FileManager:
    """管理用例文件系统的所有操作"""
    
    def __init__(self):
        """初始化文件管理器，设置存储根目录"""
        self.storage_root = Path(settings.MEDIA_ROOT) / STORAGE_ROOT_NAME
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self) -> None:
        """确保存储目录存在"""
        try:
            self.storage_root.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Storage root ensured: {self.storage_root}")
        except Exception as e:
            logger.error(f"Failed to create storage root: {e}")
            raise FileOperationException("create_directory", str(self.storage_root), str(e))
    
    def get_abs_path(self, relative_path: str) -> Path:
        """
        将相对路径转换为绝对路径
        
        Args:
            relative_path: 从存储根目录开始的相对路径
            
        Returns:
            绝对路径 Path 对象
            
        Raises:
            PathTraversalException: 如果路径在存储根目录之外
        """
        # 移除前导斜杠
        relative_path = relative_path.lstrip('/')
        
        # 检查禁止的模式
        for pattern in FORBIDDEN_FILE_PATTERNS:
            if pattern in relative_path:
                raise PathTraversalException(relative_path)
        
        abs_path = self.storage_root / relative_path
        
        # 安全检查：确保路径在存储根目录内
        try:
            abs_path.resolve().relative_to(self.storage_root.resolve())
        except ValueError:
            raise PathTraversalException(relative_path)
        
        return abs_path
    
    def get_relative_path(self, abs_path: Path) -> str:
        """
        将绝对路径转换为相对路径
        
        Args:
            abs_path: 绝对路径 Path 对象
            
        Returns:
            带前导斜杠的相对路径字符串
        """
        try:
            rel_path = abs_path.relative_to(self.storage_root)
            return f"/{rel_path.as_posix()}"
        except ValueError:
            logger.warning(f"Path {abs_path} is outside storage root")
            return "/"
    
    def get_casespaces(self) -> List[Dict[str, str]]:
        """
        获取所有 Casespace 列表
        
        Returns:
            Casespace 字典列表，包含 'name' 和 'path'
        """
        casespaces = []
        try:
            if not self.storage_root.exists():
                logger.warning(f"Storage root does not exist: {self.storage_root}")
                return casespaces
                
            for item in sorted(self.storage_root.iterdir(), key=lambda x: x.name.lower()):
                if item.is_dir() and not item.name.startswith('.'):
                    casespaces.append({
                        'name': item.name,
                        'path': item.name
                    })
            
            logger.debug(f"Found {len(casespaces)} casespaces")
        except Exception as e:
            logger.error(f"Error scanning casespaces: {e}")
        
        return casespaces
    
    def get_cases(self, casespace: str) -> List[Dict[str, str]]:
        """
        获取指定 Casespace 下的所有 Case 列表
        
        Args:
            casespace: Casespace 目录名称
            
        Returns:
            Case 字典列表，包含 'name' 和 'path'
            
        Raises:
            CasespaceNotFoundException: 如果 Casespace 不存在
        """
        cases = []
        casespace_path = self.storage_root / casespace
        
        if not casespace_path.exists():
            raise CasespaceNotFoundException(casespace)
        
        if not casespace_path.is_dir():
            logger.error(f"Casespace path is not a directory: {casespace_path}")
            return cases
        
        try:
            for item in sorted(casespace_path.iterdir(), key=lambda x: x.name.lower()):
                if item.is_dir() and not item.name.startswith('.'):
                    cases.append({
                        'name': item.name,
                        'path': f"{casespace}/{item.name}"
                    })
            
            logger.debug(f"Found {len(cases)} cases in casespace '{casespace}'")
        except Exception as e:
            logger.error(f"Error scanning cases in {casespace}: {e}")
        
        return cases
    
    def get_file_tree(
        self,
        root_path: str = "/",
        casespace: Optional[str] = None,
        case: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取文件树结构
        
        Args:
            root_path: 起始路径
            casespace: Casespace 名称（可选）
            case: Case 名称（可选）
            
        Returns:
            文件节点字典列表
        """
        # 如果提供了 casespace 和 case，调整根路径
        if casespace and case:
            root_path = f"/{casespace}/{case}{root_path}" if root_path != "/" else f"/{casespace}/{case}"
        
        abs_path = self.get_abs_path(root_path)
        
        if not abs_path.exists():
            logger.warning(f"Path does not exist: {abs_path}")
            return []
        
        if abs_path.is_file():
            return [{
                'path': self.get_relative_path(abs_path),
                'name': abs_path.name,
                'type': 'file'
            }]
        
        # 这是一个目录
        return self._get_children(abs_path)
    
    def _get_children(self, dir_path: Path) -> List[Dict[str, Any]]:
        """
        递归获取目录的子节点
        
        Args:
            dir_path: 目录路径
            
        Returns:
            子节点字典列表
        """
        children = []
        try:
            # 目录优先排序，然后按名称排序
            items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if item.name.startswith('.'):
                    continue  # 跳过隐藏文件
                
                rel_path = self.get_relative_path(item)
                
                if item.is_dir():
                    node = {
                        'path': rel_path,
                        'name': item.name,
                        'type': 'folder',
                        'children': self._get_children(item)
                    }
                else:
                    node = {
                        'path': rel_path,
                        'name': item.name,
                        'type': 'file'
                    }
                
                children.append(node)
        except PermissionError as e:
            logger.warning(f"Permission denied accessing directory: {dir_path}")
        except Exception as e:
            logger.error(f"Error reading directory {dir_path}: {e}")
        
        return children
    
    def get_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        读取文件内容
        
        Args:
            file_path: 相对文件路径
            
        Returns:
            包含 path, content, language 的字典
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 路径不是文件
        """
        abs_path = self.get_abs_path(file_path)
        
        if not abs_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        if not abs_path.is_file():
            raise ValueError(f"{file_path} is not a file")
        
        try:
            content = abs_path.read_text(encoding=DEFAULT_ENCODING)
        except UnicodeDecodeError:
            # 尝试使用备用编码
            logger.debug(f"UTF-8 decode failed, trying {FALLBACK_ENCODING}")
            content = abs_path.read_text(encoding=FALLBACK_ENCODING)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise FileOperationException("read", file_path, str(e))
        
        language = self._get_language_from_filename(abs_path.name)
        
        return {
            'path': file_path,
            'content': content,
            'language': language
        }
    
    def save_file(self, file_path: str, content: str) -> bool:
        """
        保存文件内容
        
        Args:
            file_path: 相对文件路径
            content: 文件内容
            
        Returns:
            成功返回 True
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 路径不是文件
        """
        abs_path = self.get_abs_path(file_path)
        
        if not abs_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        
        if not abs_path.is_file():
            raise ValueError(f"{file_path} is not a file")
        
        try:
            abs_path.write_text(content, encoding=DEFAULT_ENCODING)
            logger.info(f"File saved successfully: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            raise FileOperationException("save", file_path, str(e))
    
    def create_file(self, parent_path: str, name: str) -> Dict[str, Any]:
        """
        创建新文件
        
        Args:
            parent_path: 父目录路径
            name: 文件名
            
        Returns:
            文件节点字典
            
        Raises:
            ValueError: 父目录不存在或不是目录
            FileExistsError: 文件已存在
        """
        parent_abs = self.get_abs_path(parent_path)
        
        if not parent_abs.exists():
            raise ValueError(f"Parent directory {parent_path} not found")
        
        if not parent_abs.is_dir():
            raise ValueError(f"{parent_path} is not a directory")
        
        file_abs = parent_abs / name
        
        if file_abs.exists():
            raise FileExistsError(f"File {name} already exists")
        
        try:
            file_abs.write_text('', encoding=DEFAULT_ENCODING)
            logger.info(f"File created: {self.get_relative_path(file_abs)}")
        except Exception as e:
            logger.error(f"Error creating file {name}: {e}")
            raise FileOperationException("create_file", name, str(e))
        
        return {
            'path': self.get_relative_path(file_abs),
            'name': name,
            'type': 'file'
        }
    
    def create_folder(self, parent_path: str, name: str) -> Dict[str, Any]:
        """
        创建新目录
        
        Args:
            parent_path: 父目录路径
            name: 目录名
            
        Returns:
            目录节点字典
            
        Raises:
            ValueError: 父目录不存在或不是目录
            FileExistsError: 目录已存在
        """
        parent_abs = self.get_abs_path(parent_path)
        
        if not parent_abs.exists():
            raise ValueError(f"Parent directory {parent_path} not found")
        
        if not parent_abs.is_dir():
            raise ValueError(f"{parent_path} is not a directory")
        
        folder_abs = parent_abs / name
        
        if folder_abs.exists():
            raise FileExistsError(f"Folder {name} already exists")
        
        try:
            folder_abs.mkdir()
            logger.info(f"Folder created: {self.get_relative_path(folder_abs)}")
        except Exception as e:
            logger.error(f"Error creating folder {name}: {e}")
            raise FileOperationException("create_folder", name, str(e))
        
        return {
            'path': self.get_relative_path(folder_abs),
            'name': name,
            'type': 'folder',
            'children': []
        }
    
    def delete_item(self, item_path: str) -> bool:
        """
        删除文件或目录
        
        Args:
            item_path: 要删除的路径
            
        Returns:
            成功返回 True
            
        Raises:
            FileNotFoundError: 项不存在
        """
        abs_path = self.get_abs_path(item_path)
        
        if not abs_path.exists():
            raise FileNotFoundError(f"Item {item_path} not found")
        
        try:
            if abs_path.is_dir():
                shutil.rmtree(abs_path)
            else:
                abs_path.unlink()
            
            logger.info(f"Item deleted: {item_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting item {item_path}: {e}")
            raise FileOperationException("delete", item_path, str(e))
    
    def rename_item(self, old_path: str, new_name: str) -> Dict[str, Any]:
        """
        重命名文件或目录
        
        Args:
            old_path: 当前路径
            new_name: 新名称（仅名称，不是完整路径）
            
        Returns:
            更新后的节点字典
            
        Raises:
            FileNotFoundError: 项不存在
            FileExistsError: 目标名称已存在
        """
        old_abs = self.get_abs_path(old_path)
        
        if not old_abs.exists():
            raise FileNotFoundError(f"Item {old_path} not found")
        
        new_abs = old_abs.parent / new_name
        
        if new_abs.exists():
            raise FileExistsError(f"Item {new_name} already exists")
        
        try:
            old_abs.rename(new_abs)
            logger.info(f"Item renamed: {old_path} -> {new_name}")
        except Exception as e:
            logger.error(f"Error renaming item {old_path}: {e}")
            raise FileOperationException("rename", old_path, str(e))
        
        return {
            'path': self.get_relative_path(new_abs),
            'name': new_name,
            'type': 'folder' if new_abs.is_dir() else 'file'
        }
    
    def upload_files(self, parent_path: str, files: List[Dict[str, str]]) -> int:
        """
        批量上传文件
        
        Args:
            parent_path: 父目录路径
            files: 文件字典列表，包含 'name' 和 'content'
            
        Returns:
            成功上传的文件数量
            
        Raises:
            ValueError: 父目录不存在或不是目录
        """
        parent_abs = self.get_abs_path(parent_path)
        
        if not parent_abs.exists():
            raise ValueError(f"Parent directory {parent_path} not found")
        
        if not parent_abs.is_dir():
            raise ValueError(f"{parent_path} is not a directory")
        
        uploaded_count = 0
        for file_item in files:
            try:
                file_abs = parent_abs / file_item['name']
                file_abs.write_text(file_item['content'], encoding=DEFAULT_ENCODING)
                uploaded_count += 1
            except Exception as e:
                logger.error(f"Error uploading file {file_item['name']}: {e}")
        
        logger.info(f"Uploaded {uploaded_count}/{len(files)} files to {parent_path}")
        return uploaded_count
    
    def delete_case(self, casespace: str, case: str) -> bool:
        """
        删除整个 Case 目录
        
        Args:
            casespace: Casespace 名称
            case: Case 名称
            
        Returns:
            成功返回 True
            
        Raises:
            CaseNotFoundException: Case 不存在
            ValueError: 路径无效
        """
        case_path = f"/{casespace}/{case}"
        case_abs = self.get_abs_path(case_path)
        
        if not case_abs.exists():
            raise CaseNotFoundException(casespace, case)
        
        if not case_abs.is_dir():
            raise ValueError(f"{case_path} is not a directory")
        
        try:
            shutil.rmtree(case_abs)
            logger.info(f"Case deleted: {casespace}/{case}")
            return True
        except Exception as e:
            logger.error(f"Error deleting case {casespace}/{case}: {e}")
            raise FileOperationException("delete_case", case_path, str(e))
    
    def download_case(self, casespace: str, case: str) -> bytes:
        """
        将 Case 打包为 zip 归档
        
        Args:
            casespace: Casespace 名称
            case: Case 名称
            
        Returns:
            zip 文件的字节数据
            
        Raises:
            CaseNotFoundException: Case 不存在
            ValueError: 路径无效
        """
        case_path = f"/{casespace}/{case}"
        case_abs = self.get_abs_path(case_path)
        
        if not case_abs.exists():
            raise CaseNotFoundException(casespace, case)
        
        if not case_abs.is_dir():
            raise ValueError(f"{case_path} is not a directory")
        
        # 创建临时 zip 文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # 创建 zip 归档
            with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(case_abs):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(case_abs)
                        zipf.write(file_path, arcname)
            
            # 读取 zip 文件
            with open(tmp_path, 'rb') as f:
                zip_data = f.read()
            
            logger.info(f"Case downloaded: {casespace}/{case}")
            return zip_data
        except Exception as e:
            logger.error(f"Error downloading case {casespace}/{case}: {e}")
            raise FileOperationException("download_case", case_path, str(e))
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def upload_case(
        self,
        casespace: str,
        case_name: str,
        file_data: bytes,
        filename: str
    ) -> bool:
        """
        上传并解压 Case 归档
        
        Args:
            casespace: Casespace 名称
            case_name: 新 Case 名称
            file_data: 归档文件字节数据
            filename: 原始文件名（用于确定格式）
            
        Returns:
            成功返回 True
            
        Raises:
            InvalidCaseNameException: Case 名称无效
            DuplicateCaseException: Case 已存在
            ValueError: 不支持的文件格式
            ArchiveExtractionException: 解压失败
        """
        # 验证 case 名称
        if not case_name or '/' in case_name or '\\' in case_name or case_name.startswith('.'):
            raise InvalidCaseNameException(case_name, "Contains invalid characters")
        
        # 检查 case 是否已存在
        case_path = f"/{casespace}/{case_name}"
        case_abs = self.get_abs_path(case_path)
        if case_abs.exists():
            raise DuplicateCaseException(casespace, case_name)
        
        # 确保 casespace 存在
        casespace_path = self.storage_root / casespace
        casespace_path.mkdir(parents=True, exist_ok=True)
        
        # 确定文件格式
        is_tar_gz = filename.endswith('.tar.gz') or filename.endswith('.tgz')
        is_zip = filename.endswith('.zip')
        
        if not (is_tar_gz or is_zip):
            raise ValueError(f"Unsupported file format. Supported formats: {', '.join(SUPPORTED_ARCHIVE_FORMATS)}")
        
        # 创建临时文件用于解压
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
            tmp_file.write(file_data)
            tmp_path = tmp_file.name
        
        try:
            # 创建 case 目录
            case_abs.mkdir(parents=True, exist_ok=True)
            
            # 解压归档
            if is_tar_gz:
                with tarfile.open(tmp_path, 'r:gz') as tar:
                    # 安全检查：确保没有路径遍历
                    for member in tar.getmembers():
                        if member.name.startswith('/') or '..' in member.name:
                            raise PathTraversalException(member.name)
                    tar.extractall(path=case_abs)
            else:  # is_zip
                with zipfile.ZipFile(tmp_path, 'r') as zip_file:
                    # 安全检查：确保没有路径遍历
                    for name in zip_file.namelist():
                        if name.startswith('/') or '..' in name:
                            raise PathTraversalException(name)
                    zip_file.extractall(path=case_abs)
            
            logger.info(f"Case uploaded: {casespace}/{case_name}")
            return True
            
        except (PathTraversalException, ValueError) as e:
            # 清理 case 目录
            if case_abs.exists():
                shutil.rmtree(case_abs)
            raise
        except Exception as e:
            # 清理 case 目录
            if case_abs.exists():
                shutil.rmtree(case_abs)
            logger.error(f"Error extracting archive: {e}")
            raise ArchiveExtractionException(filename, str(e))
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _get_language_from_filename(self, filename: str) -> Optional[str]:
        """
        根据文件扩展名获取编程语言
        
        Args:
            filename: 文件名
            
        Returns:
            语言标识符或 None
        """
        ext = Path(filename).suffix.lower()
        return LANGUAGE_EXTENSION_MAP.get(ext)


# 创建全局 file_manager 实例
file_manager = FileManager()

