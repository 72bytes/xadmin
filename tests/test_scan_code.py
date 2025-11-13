"""
代码扫描测试

测试项目中各种格式文件的代码质量和规范性
支持的文件格式：
1. Python (.py)
2. Vue (.vue)
3. TypeScript/JavaScript (.ts, .js)
4. HTML (.html)
5. JSON (.json)
6. XML (.xml)
7. Shell (.sh)
8. 配置文件 (.ini, .toml)
"""

import os
import json
import ast
import re
import pytest
from pathlib import Path
from typing import List, Tuple
import xml.etree.ElementTree as ET


class TestCodeScan:
    """代码扫描基础测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """设置测试环境"""
        self.project_root = Path(__file__).parent.parent
        self.web_root = self.project_root / "web"
        
        # 排除的目录
        self.exclude_dirs = {
            '__pycache__', '.pytest_cache', 'node_modules', '.git', 
            '.venv', 'venv', 'dist', 'build', 'htmlcov', 'logs',
            '__pypackages__', '.eggs', '*.egg-info'
        }
        
        print(f"\n📂 项目根目录: {self.project_root}")
        print(f"📂 前端根目录: {self.web_root}")
    
    def _should_exclude(self, path: Path) -> bool:
        """判断路径是否应该被排除"""
        return any(excluded in path.parts for excluded in self.exclude_dirs)
    
    def _find_files(self, pattern: str, root: Path = None) -> List[Path]:
        """查找指定格式的文件"""
        if root is None:
            root = self.project_root
        
        files = []
        for file in root.rglob(pattern):
            if not self._should_exclude(file):
                files.append(file)
        return files


class TestPythonCodeScan(TestCodeScan):
    """Python 代码扫描测试"""
    
    def test_python_files_exist(self):
        """测试 Python 文件是否存在"""
        py_files = self._find_files("*.py")
        assert len(py_files) > 0, "❌ 未找到 Python 文件"
        print(f"\n✅ 找到 {len(py_files)} 个 Python 文件")
    
    def test_python_syntax_valid(self):
        """测试 Python 文件语法是否正确"""
        py_files = self._find_files("*.py")
        invalid_files = []
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    ast.parse(content)
            except SyntaxError as e:
                invalid_files.append((py_file, str(e)))
            except Exception as e:
                # 忽略编码等其他错误
                pass
        
        if invalid_files:
            error_msg = "\n".join([f"  {file}: {error}" for file, error in invalid_files])
            pytest.fail(f"❌ 发现 {len(invalid_files)} 个语法错误的 Python 文件:\n{error_msg}")
        
        print(f"✅ 所有 {len(py_files)} 个 Python 文件语法正确")
    
    def test_python_encoding(self):
        """测试 Python 文件编码是否为 UTF-8"""
        py_files = self._find_files("*.py")
        encoding_errors = []
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError:
                encoding_errors.append(py_file)
        
        if encoding_errors:
            error_msg = "\n".join([f"  {file}" for file in encoding_errors])
            pytest.fail(f"❌ 发现 {len(encoding_errors)} 个编码错误的文件:\n{error_msg}")
        
        print(f"✅ 所有 {len(py_files)} 个 Python 文件编码正确 (UTF-8)")
    
    def test_python_imports(self):
        """测试 Python 文件导入语句规范"""
        py_files = self._find_files("*.py")
        issues = []
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        # 检查是否有 import *
                        if isinstance(node, ast.ImportFrom):
                            if any(alias.name == '*' for alias in node.names):
                                issues.append(f"{py_file}: 使用了 'from ... import *'")
            except Exception:
                # 跳过无法解析的文件
                pass
        
        # 这里只是警告，不阻止测试通过
        if issues:
            print(f"\n⚠️  发现 {len(issues)} 个导入规范建议:")
            for issue in issues[:10]:  # 只显示前10个
                print(f"  {issue}")
        else:
            print(f"✅ Python 导入语句规范")


class TestFrontendCodeScan(TestCodeScan):
    """前端代码扫描测试"""
    
    def test_vue_files_exist(self):
        """测试 Vue 文件是否存在"""
        if not self.web_root.exists():
            pytest.skip("前端目录不存在")
        
        vue_files = self._find_files("*.vue", self.web_root)
        assert len(vue_files) > 0, "❌ 未找到 Vue 文件"
        print(f"\n✅ 找到 {len(vue_files)} 个 Vue 文件")
    
    def test_vue_file_structure(self):
        """测试 Vue 文件结构是否正确"""
        if not self.web_root.exists():
            pytest.skip("前端目录不存在")
        
        vue_files = self._find_files("*.vue", self.web_root)
        invalid_files = []
        
        for vue_file in vue_files:
            try:
                with open(vue_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 检查基本的 Vue 文件结构
                    if not re.search(r'<template>', content, re.IGNORECASE):
                        if not re.search(r'<script', content, re.IGNORECASE):
                            invalid_files.append(f"{vue_file}: 缺少 template 或 script 标签")
            except Exception as e:
                invalid_files.append(f"{vue_file}: {str(e)}")
        
        if invalid_files:
            error_msg = "\n".join([f"  {error}" for error in invalid_files[:10]])
            pytest.fail(f"❌ 发现 {len(invalid_files)} 个结构问题的 Vue 文件:\n{error_msg}")
        
        print(f"✅ 所有 {len(vue_files)} 个 Vue 文件结构正确")
    
    def test_typescript_javascript_files(self):
        """测试 TypeScript/JavaScript 文件"""
        if not self.web_root.exists():
            pytest.skip("前端目录不存在")
        
        ts_files = self._find_files("*.ts", self.web_root)
        js_files = self._find_files("*.js", self.web_root)
        total_files = len(ts_files) + len(js_files)
        
        assert total_files > 0, "❌ 未找到 TypeScript/JavaScript 文件"
        print(f"\n✅ 找到 {len(ts_files)} 个 TypeScript 文件和 {len(js_files)} 个 JavaScript 文件")
    
    def test_html_files(self):
        """测试 HTML 文件"""
        html_files = self._find_files("*.html")
        
        if len(html_files) == 0:
            pytest.skip("未找到 HTML 文件")
        
        print(f"\n✅ 找到 {len(html_files)} 个 HTML 文件")


class TestConfigFileScan(TestCodeScan):
    """配置文件扫描测试"""
    
    def test_json_files_valid(self):
        """测试 JSON 文件是否有效"""
        json_files = self._find_files("*.json")
        
        # JSONC 文件（支持注释的 JSON）列表，这些文件应该被排除
        jsonc_patterns = [
            'tsconfig.json',
            'jsconfig.json',
            '.vscode/settings.json',
            '.vscode/launch.json',
            '.vscode/tasks.json',
        ]
        
        # 过滤掉 JSONC 文件
        filtered_files = []
        for json_file in json_files:
            file_str = str(json_file)
            if not any(pattern in file_str for pattern in jsonc_patterns):
                filtered_files.append(json_file)
        
        invalid_files = []
        
        for json_file in filtered_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                invalid_files.append((json_file, str(e)))
            except Exception:
                pass
        
        if invalid_files:
            error_msg = "\n".join([f"  {file}: {error}" for file, error in invalid_files[:10]])
            pytest.fail(f"❌ 发现 {len(invalid_files)} 个无效的 JSON 文件:\n{error_msg}")
        
        excluded_count = len(json_files) - len(filtered_files)
        print(f"✅ 所有 {len(filtered_files)} 个 JSON 文件格式正确 (排除了 {excluded_count} 个 JSONC 文件)")
    
    def test_xml_files_valid(self):
        """测试 XML 文件是否有效"""
        xml_files = self._find_files("*.xml")
        
        if len(xml_files) == 0:
            pytest.skip("未找到 XML 文件")
        
        invalid_files = []
        for xml_file in xml_files:
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    ET.parse(f)
            except ET.ParseError as e:
                invalid_files.append((xml_file, str(e)))
            except Exception:
                pass
        
        if invalid_files:
            error_msg = "\n".join([f"  {file}: {error}" for file, error in invalid_files])
            pytest.fail(f"❌ 发现 {len(invalid_files)} 个无效的 XML 文件:\n{error_msg}")
        
        print(f"✅ 所有 {len(xml_files)} 个 XML 文件格式正确")
    
    def test_ini_files_exist(self):
        """测试 INI 配置文件"""
        ini_files = self._find_files("*.ini")
        
        if len(ini_files) == 0:
            pytest.skip("未找到 INI 文件")
        
        print(f"\n✅ 找到 {len(ini_files)} 个 INI 配置文件")
        for ini_file in ini_files:
            print(f"  - {ini_file.relative_to(self.project_root)}")
    
    def test_toml_files_exist(self):
        """测试 TOML 配置文件"""
        toml_files = self._find_files("*.toml")
        
        if len(toml_files) == 0:
            pytest.skip("未找到 TOML 文件")
        
        print(f"\n✅ 找到 {len(toml_files)} 个 TOML 配置文件")
        for toml_file in toml_files:
            print(f"  - {toml_file.relative_to(self.project_root)}")


class TestShellScriptScan(TestCodeScan):
    """Shell 脚本扫描测试"""
    
    def test_shell_scripts_exist(self):
        """测试 Shell 脚本是否存在"""
        sh_files = self._find_files("*.sh")
        
        if len(sh_files) == 0:
            pytest.skip("未找到 Shell 脚本")
        
        assert len(sh_files) > 0, "❌ 未找到 Shell 脚本"
        print(f"\n✅ 找到 {len(sh_files)} 个 Shell 脚本")
    
    def test_shell_scripts_executable(self):
        """测试 Shell 脚本是否有执行权限"""
        sh_files = self._find_files("*.sh")
        
        if len(sh_files) == 0:
            pytest.skip("未找到 Shell 脚本")
        
        non_executable = []
        for sh_file in sh_files:
            if not os.access(sh_file, os.X_OK):
                non_executable.append(sh_file)
        
        if non_executable:
            warning_msg = "\n".join([f"  {file.relative_to(self.project_root)}" for file in non_executable])
            print(f"\n⚠️  发现 {len(non_executable)} 个没有执行权限的 Shell 脚本:")
            print(warning_msg)
            print("  提示: 使用 'chmod +x <file>' 添加执行权限")
        else:
            print(f"✅ 所有 {len(sh_files)} 个 Shell 脚本都有执行权限")
    
    def test_shell_scripts_shebang(self):
        """测试 Shell 脚本是否有正确的 shebang"""
        sh_files = self._find_files("*.sh")
        
        if len(sh_files) == 0:
            pytest.skip("未找到 Shell 脚本")
        
        missing_shebang = []
        for sh_file in sh_files:
            try:
                with open(sh_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if not first_line.startswith('#!'):
                        missing_shebang.append(sh_file)
            except Exception:
                pass
        
        if missing_shebang:
            warning_msg = "\n".join([f"  {file.relative_to(self.project_root)}" for file in missing_shebang])
            print(f"\n⚠️  发现 {len(missing_shebang)} 个缺少 shebang 的 Shell 脚本:")
            print(warning_msg)
        else:
            print(f"✅ 所有 {len(sh_files)} 个 Shell 脚本都有 shebang")


class TestCodeQualityScan(TestCodeScan):
    """代码质量扫描测试"""
    
    def test_file_encoding_consistency(self):
        """测试文件编码一致性"""
        patterns = ["*.py", "*.js", "*.ts", "*.vue", "*.json", "*.xml", "*.sh"]
        all_files = []
        
        for pattern in patterns:
            all_files.extend(self._find_files(pattern))
        
        encoding_errors = []
        for file in all_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    f.read()
            except UnicodeDecodeError:
                encoding_errors.append(file)
        
        if encoding_errors:
            error_msg = "\n".join([f"  {file.relative_to(self.project_root)}" for file in encoding_errors])
            pytest.fail(f"❌ 发现 {len(encoding_errors)} 个编码错误的文件:\n{error_msg}")
        
        print(f"✅ 所有 {len(all_files)} 个代码文件编码一致 (UTF-8)")
    
    def test_no_trailing_whitespace_in_python(self):
        """测试 Python 文件是否有行尾空白"""
        py_files = self._find_files("*.py")
        files_with_trailing = []
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if line.rstrip('\n') != line.rstrip():
                            files_with_trailing.append((py_file, i))
                            break  # 只记录第一个问题行
            except Exception:
                pass
        
        if files_with_trailing:
            warning_msg = "\n".join([f"  {file.relative_to(self.project_root)}:{line}" 
                                    for file, line in files_with_trailing[:10]])
            print(f"\n⚠️  发现 {len(files_with_trailing)} 个 Python 文件有行尾空白:")
            print(warning_msg)
        else:
            print(f"✅ 所有 Python 文件没有行尾空白")
    
    def test_project_structure(self):
        """测试项目基本结构"""
        required_items = [
            ("xadmin", "后端主应用目录"),
            ("web", "前端项目目录"),
            ("tests", "测试目录"),
            (".venv", "Python 虚拟环境"),
        ]
        
        missing = []
        for item, desc in required_items:
            if not (self.project_root / item).exists():
                missing.append(f"{item} ({desc})")
        
        if missing:
            error_msg = "\n".join([f"  {item}" for item in missing])
            pytest.fail(f"❌ 缺少必要的项目结构:\n{error_msg}")
        
        print("✅ 项目基本结构完整")
        for item, desc in required_items:
            print(f"  - {item}: {desc}")


class TestCodeStatistics(TestCodeScan):
    """代码统计测试"""
    
    def test_code_statistics(self):
        """统计项目代码文件数量"""
        stats = {
            "Python": len(self._find_files("*.py")),
            "Vue": len(self._find_files("*.vue", self.web_root)) if self.web_root.exists() else 0,
            "TypeScript": len(self._find_files("*.ts", self.web_root)) if self.web_root.exists() else 0,
            "JavaScript": len(self._find_files("*.js", self.web_root)) if self.web_root.exists() else 0,
            "JSON": len(self._find_files("*.json")),
            "XML": len(self._find_files("*.xml")),
            "Shell": len(self._find_files("*.sh")),
            "INI": len(self._find_files("*.ini")),
            "TOML": len(self._find_files("*.toml")),
        }
        
        print("\n📊 项目代码文件统计:")
        total = 0
        for file_type, count in stats.items():
            if count > 0:
                print(f"  - {file_type}: {count} 个文件")
                total += count
        
        print(f"\n  总计: {total} 个代码文件")
        assert total > 0, "❌ 未找到任何代码文件"
    
    def test_code_lines_count(self):
        """统计代码行数（Python 文件）"""
        py_files = self._find_files("*.py")
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        total_lines += 1
                        stripped = line.strip()
                        if not stripped:
                            blank_lines += 1
                        elif stripped.startswith('#'):
                            comment_lines += 1
                        else:
                            code_lines += 1
            except Exception:
                pass
        
        print(f"\n📏 Python 代码行数统计:")
        print(f"  - 总行数: {total_lines}")
        print(f"  - 代码行: {code_lines} ({code_lines/total_lines*100:.1f}%)" if total_lines > 0 else "")
        print(f"  - 注释行: {comment_lines} ({comment_lines/total_lines*100:.1f}%)" if total_lines > 0 else "")
        print(f"  - 空白行: {blank_lines} ({blank_lines/total_lines*100:.1f}%)" if total_lines > 0 else "")
        
        assert total_lines > 0, "❌ 未统计到任何代码行"

