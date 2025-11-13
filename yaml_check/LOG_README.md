# YAML Check 日志功能说明

## 概述

已为 `yaml_check` 模块添加了完整的日志功能，所有日志输出到专用日志文件。

## 日志配置

### 日志文件位置
- **日志文件**: `/home/zx/xadmin_zx/logs/yaml_check.log`
- **自动创建**: 如果 `logs` 文件夹不存在，会自动创建

### 日志格式

**控制台输出格式** (开发环境)：
```
2025-11-12 14:30:00 | INFO     | yaml_check | 收到 YAML 验证请求
```

**文件输出格式**：
```
2025-11-12 14:30:00.123 | INFO     | yaml_check.views:validate_yaml:42 | 收到 YAML 验证请求
```

### 日志轮转配置
- **文件大小**: 10 MB 时自动轮转
- **保留时间**: 30 天
- **压缩方式**: ZIP 压缩旧日志
- **编码**: UTF-8

## 日志级别

系统使用以下日志级别：

| 级别 | 说明 | 使用场景 |
|------|------|---------|
| DEBUG | 调试信息 | 详细的执行流程、变量值 |
| INFO | 一般信息 | 正常的业务流程、验证通过 |
| WARNING | 警告信息 | 验证失败、数据异常 |
| ERROR | 错误信息 | 系统错误、解析失败 |
| EXCEPTION | 异常信息 | 包含完整堆栈信息的异常 |
| SUCCESS | 成功信息 | 所有验证通过 |

## 日志内容

### views.py 日志

#### 请求处理
```python
INFO  : 收到 YAML 验证请求
DEBUG : 开始验证 YAML 数据，数据键: ['metadata', 'hardware', 'environment']
INFO  : 验证完成，结果: 成功/失败
INFO  : 返回验证结果
```

#### 错误处理
```python
WARNING : 请求体中缺少 yamlData
WARNING : 验证失败: [E002] E002 Unsupported: empty value for [hardware.machines]
ERROR   : JSON 解析失败: Expecting value: line 1 column 1 (char 0)
EXCEPTION : 验证过程发生异常: division by zero
```

#### 行号查找
```python
DEBUG : 提取到错误 key 路径: hardware.machines
INFO  : 找到错误行号: 7, key: hardware.machines
WARNING : 未能找到 key 的行号: hardware.unknown
```

### validator.py 日志

#### 主验证流程
```python
INFO  : ========== 开始 YAML 验证流程 ==========
DEBUG : 开始 E001 验证：检查必需键 ['hardware.cpu', 'hardware.gpu']
INFO  : ✅ E001 验证通过：所有必需键存在
DEBUG : 开始 E002 验证：检查空值
DEBUG : 扁平化后共 15 个字段
INFO  : ✅ E002 验证通过：所有字段非空
DEBUG : 开始 E101 验证：检查值类型
INFO  : ✅ E101 验证通过：值类型正确
DEBUG : 开始 E102 验证：检查值范围
INFO  : ✅ E102 验证通过：值范围合法
SUCCESS : ========== ✅ 所有验证通过 ==========
```

#### 验证失败
```python
WARNING : E001: 缺少必需键 [hardware.cpu]
WARNING : E002: 字段 [hardware.machines] 值为空: []
WARNING : E101: 类型验证失败 - E101 Unsupported: value type error for [hardware.cpu]. Expected string, got int
WARNING : E102: 范围验证失败 - E102 Unsupported: invalid value range for [hardware.cpu]
ERROR   : E000: 无效的 YAML 数据对象
EXCEPTION : 验证过程发生异常: 'NoneType' object is not iterable
```

### line_finder.py 日志

```python
DEBUG : 查找 key 行号: hardware.machines
DEBUG : YAML 文本共 42 行，key 路径层级: ['hardware', 'machines']
DEBUG : 匹配到 key 'hardware' 在第 5 行
DEBUG : 匹配到 key 'machines' 在第 7 行
INFO  : 找到完整 key 路径 'hardware.machines' 在第 7 行
WARNING : 未找到 key 路径: hardware.unknown
```

## 使用说明

### 查看日志

**实时查看日志**：
```bash
tail -f /home/zx/xadmin_zx/logs/yaml_check.log
```

**查看最近100行**：
```bash
tail -n 100 /home/zx/xadmin_zx/logs/yaml_check.log
```

**搜索特定错误**：
```bash
grep "E002" /home/zx/xadmin_zx/logs/yaml_check.log
grep "ERROR" /home/zx/xadmin_zx/logs/yaml_check.log
grep "EXCEPTION" /home/zx/xadmin_zx/logs/yaml_check.log
```

**按日期查看**：
```bash
grep "2025-11-12" /home/zx/xadmin_zx/logs/yaml_check.log
```

### 调整日志级别

编辑 `/home/zx/xadmin_zx/yaml_check/logger.py`：

```python
# 控制台日志级别（开发环境）
yaml_check_logger.add(
    sys.stdout,
    level="DEBUG",  # 改为 "INFO" 减少输出
    ...
)

# 文件日志级别（生产环境）
yaml_check_logger.add(
    str(LOG_FILE),
    level="INFO",  # 改为 "WARNING" 只记录警告和错误
    ...
)
```

### 启用调试模式

在 `validator.py` 中设置：

```python
def validate_mandatory_non_empty_keys(self, yaml_data):
    # 设为 True 启用详细调试信息
    DEBUG_MODE = True
```

启用后会输出：
- 完整的 YAML 数据结构
- 扁平化后的所有字段
- 临时 JSON 文件保存到 `/tmp/yaml_data_YYYYMMDD_HHMMSS.json`

## 日志文件管理

### 清理旧日志

**手动清理**：
```bash
# 删除30天前的日志
find /home/zx/xadmin_zx/logs -name "yaml_check.log.*" -mtime +30 -delete
```

**查看日志文件大小**：
```bash
ls -lh /home/zx/xadmin_zx/logs/yaml_check.log*
```

### 自动压缩

日志系统会自动压缩轮转的日志文件：
- `yaml_check.log` - 当前日志
- `yaml_check.log.2025-11-12_14-30.zip` - 已压缩的历史日志

## 性能考虑

### 生产环境建议

1. **调整文件日志级别为 INFO**
   ```python
   level="INFO"  # 不记录 DEBUG 信息
   ```

2. **减少控制台输出**
   ```python
   # 生产环境可以注释掉控制台输出
   # yaml_check_logger.add(sys.stdout, ...)
   ```

3. **调整轮转大小**
   ```python
   rotation="50 MB"  # 增大轮转大小，减少文件数量
   ```

4. **缩短保留时间**
   ```python
   retention="7 days"  # 减少保留时间，节省磁盘空间
   ```

## 故障排查

### 常见问题

**Q: 日志文件没有生成？**
A: 检查以下几点：
- logs 目录是否存在且有写入权限
- Django 进程是否有权限创建文件
- 是否有磁盘空间

**Q: 日志级别太详细/太简略？**
A: 编辑 `yaml_check/logger.py` 调整 `level` 参数

**Q: 如何调试特定请求？**
A: 
1. 设置 `DEBUG_MODE = True`
2. 查看 `/tmp/yaml_data_*.json` 文件
3. 检查详细的日志输出

**Q: 日志文件太大？**
A: 
- 检查是否有异常的大量请求
- 调整 `rotation` 参数
- 减少保留时间

## 日志示例

### 成功验证的完整日志

```
2025-11-12 14:30:00.123 | INFO     | yaml_check.views:validate_yaml:42 | 收到 YAML 验证请求
2025-11-12 14:30:00.125 | DEBUG    | yaml_check.views:validate_yaml:54 | 开始验证 YAML 数据，数据键: ['metadata', 'hardware', 'environment', 'firmware', 'test_suites']
2025-11-12 14:30:00.126 | INFO     | yaml_check.validator:validate:262 | ========== 开始 YAML 验证流程 ==========
2025-11-12 14:30:00.127 | DEBUG    | yaml_check.validator:validate_required_root_keys:81 | 开始 E001 验证：检查必需键 ['hardware.cpu', 'hardware.gpu']
2025-11-12 14:30:00.128 | INFO     | yaml_check.validator:validate_required_root_keys:99 | ✅ E001 验证通过：所有必需键存在
2025-11-12 14:30:00.129 | DEBUG    | yaml_check.validator:validate_mandatory_non_empty_keys:108 | 开始 E002 验证：检查空值
2025-11-12 14:30:00.130 | DEBUG    | yaml_check.validator:validate_mandatory_non_empty_keys:129 | 扁平化后共 15 个字段
2025-11-12 14:30:00.145 | INFO     | yaml_check.validator:validate_mandatory_non_empty_keys:158 | ✅ E002 验证通过：所有字段非空
2025-11-12 14:30:00.146 | DEBUG    | yaml_check.validator:validate:298 | 开始 E101 验证：检查值类型
2025-11-12 14:30:00.147 | INFO     | yaml_check.validator:validate:309 | ✅ E101 验证通过：值类型正确
2025-11-12 14:30:00.148 | DEBUG    | yaml_check.validator:validate:312 | 开始 E102 验证：检查值范围
2025-11-12 14:30:00.149 | INFO     | yaml_check.validator:validate:323 | ✅ E102 验证通过：值范围合法
2025-11-12 14:30:00.150 | SUCCESS  | yaml_check.validator:validate:326 | ========== ✅ 所有验证通过 ==========
2025-11-12 14:30:00.151 | INFO     | yaml_check.views:validate_yaml:60 | 验证完成，结果: 成功
2025-11-12 14:30:00.152 | INFO     | yaml_check.views:validate_yaml:94 | 返回验证结果
```

### 验证失败的完整日志

```
2025-11-12 14:35:00.123 | INFO     | yaml_check.views:validate_yaml:42 | 收到 YAML 验证请求
2025-11-12 14:35:00.125 | DEBUG    | yaml_check.views:validate_yaml:54 | 开始验证 YAML 数据，数据键: ['metadata', 'hardware', 'environment']
2025-11-12 14:35:00.126 | INFO     | yaml_check.validator:validate:262 | ========== 开始 YAML 验证流程 ==========
2025-11-12 14:35:00.127 | DEBUG    | yaml_check.validator:validate_required_root_keys:81 | 开始 E001 验证：检查必需键 ['hardware.cpu', 'hardware.gpu']
2025-11-12 14:35:00.128 | INFO     | yaml_check.validator:validate_required_root_keys:99 | ✅ E001 验证通过：所有必需键存在
2025-11-12 14:35:00.129 | DEBUG    | yaml_check.validator:validate_mandatory_non_empty_keys:108 | 开始 E002 验证：检查空值
2025-11-12 14:35:00.130 | DEBUG    | yaml_check.validator:validate_mandatory_non_empty_keys:129 | 扁平化后共 12 个字段
2025-11-12 14:35:00.131 | WARNING  | yaml_check.validator:validate_mandatory_non_empty_keys:151 | E002: 字段 [hardware.machines] 值为空: []
2025-11-12 14:35:00.132 | INFO     | yaml_check.views:validate_yaml:60 | 验证完成，结果: 失败
2025-11-12 14:35:00.133 | WARNING  | yaml_check.views:validate_yaml:68 | 验证失败: [E002] E002 Unsupported: empty value for [hardware.machines]
2025-11-12 14:35:00.134 | DEBUG    | yaml_check.views:validate_yaml:76 | 提取到错误 key 路径: hardware.machines
2025-11-12 14:35:00.135 | DEBUG    | yaml_check.line_finder:find_key_line_number:33 | 查找 key 行号: hardware.machines
2025-11-12 14:35:00.136 | DEBUG    | yaml_check.line_finder:find_key_line_number:42 | YAML 文本共 42 行，key 路径层级: ['hardware', 'machines']
2025-11-12 14:35:00.138 | DEBUG    | yaml_check.line_finder:find_key_line_number:69 | 匹配到 key 'hardware' 在第 5 行
2025-11-12 14:35:00.139 | DEBUG    | yaml_check.line_finder:find_key_line_number:69 | 匹配到 key 'machines' 在第 7 行
2025-11-12 14:35:00.140 | INFO     | yaml_check.line_finder:find_key_line_number:73 | 找到完整 key 路径 'hardware.machines' 在第 7 行
2025-11-12 14:35:00.141 | INFO     | yaml_check.views:validate_yaml:87 | 找到错误行号: 7, key: hardware.machines
2025-11-12 14:35:00.142 | INFO     | yaml_check.views:validate_yaml:94 | 返回验证结果
```

## 技术细节

### Logger 实现
- 基于 `loguru` 库
- 使用 `bind(module='yaml_check')` 标记模块
- 支持彩色输出和完整的异常堆栈

### 集成方式
- 在每个模块导入: `from .logger import yaml_check_logger`
- 使用统一的 logger 实例
- 自动添加模块、函数、行号信息

### 线程安全
- loguru 默认线程安全
- 支持多进程环境
- 文件写入有锁保护

---

**文档版本**: 1.0  
**更新日期**: 2025-11-12  
**维护者**: System

