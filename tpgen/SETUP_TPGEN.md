# tpgen App 设置步骤

## 当前状态

✅ tpgen app 已创建  
✅ models.py 已完成（8个模型）  
✅ schemas.py 已完成（16个schemas）  
✅ settings.py 已配置多数据库  
✅ database_router.py 已创建  
✅ tpdb 数据库已创建  

---

## manage.py 执行步骤

### 1️⃣ 检查配置（可选但推荐）

```bash
# 检查项目配置是否正确
python manage.py check

# 检查特定 app
python manage.py check tpgen
```

**预期输出**: `System check identified no issues (0 silenced).`

---

### 2️⃣ 创建迁移文件

```bash
# 为 tpgen 创建迁移
python manage.py makemigrations tpgen
```

**预期输出**:
```
Migrations for 'tpgen':
  tpgen/migrations/0001_initial.py
    - Create model SutDevice
    - Create model OsConfig
    - Create model TestType
    - Create model OsSupportedKernel
    - Create model TestComponent
    - Create model TestCase
    - Create model TestPlan
    - Create model TestPlanCase
```

**注意**: 如果迁移文件已存在，会显示 `No changes detected in app 'tpgen'`

---

### 3️⃣ 查看迁移SQL（可选）

```bash
# 查看迁移将执行的SQL语句
python manage.py sqlmigrate tpgen 0001
```

这会显示将要执行的 CREATE TABLE 等 SQL 语句，用于确认迁移内容。

---

### 4️⃣ 查看迁移状态

```bash
# 查看所有迁移状态
python manage.py showmigrations

# 只查看 tpgen 的迁移状态
python manage.py showmigrations tpgen

# 指定数据库
python manage.py showmigrations tpgen --database=tpdb
```

**预期输出**:
```
tpgen
 [ ] 0001_initial
```

`[ ]` 表示未应用，`[X]` 表示已应用

---

### 5️⃣ 应用迁移到 tpdb 数据库 ⭐ 核心步骤

```bash
# 方式1: 只迁移 tpgen 到 tpdb（推荐）
python manage.py migrate tpgen --database=tpdb

# 方式2: 迁移所有应用到对应数据库（路由器自动处理）
python manage.py migrate
```

**预期输出**:
```
Operations to perform:
  Apply all migrations: tpgen
Running migrations:
  Applying tpgen.0001_initial... OK
```

**结果**: 在 tpdb 数据库中创建 8 个数据表

---

### 6️⃣ 验证迁移结果

#### 方法A: 使用 Django Shell

```bash
python manage.py shell
```

```python
# 在 shell 中执行
from tpgen.models import SutDevice, OsConfig, TestPlan

# 查看模型（应该返回空列表，因为还没数据）
print(SutDevice.objects.count())  # 输出: 0
print(OsConfig.objects.count())   # 输出: 0
print(TestPlan.objects.count())   # 输出: 0

# 测试创建
device = SutDevice.objects.create(
    hostname='test-device',
    gpu_model='RX 7900 XTX'
)
print(device.id)  # 应该输出: 1

# 清理测试数据
device.delete()
```

#### 方法B: 使用 dbshell

```bash
# 连接到 tpdb 数据库
python manage.py dbshell --database=tpdb
```

```sql
-- 在 psql 中执行
\dt  -- 查看所有表

-- 应该看到以下表：
-- sut_devices
-- os_configs
-- os_supported_kernels
-- test_types
-- test_components
-- test_cases
-- test_plans
-- test_plan_cases
-- django_migrations

\q  -- 退出
```

#### 方法C: 直接 psql 连接

```bash
PGPASSWORD='amdyes' psql -U amd -h 127.0.0.1 -p 5432 -d tpdb -c "\dt"
```

---

### 7️⃣ 导入测试数据（可选）

```bash
# 方式1: 使用提供的脚本
chmod +x import_to_tpdb.sh
./import_to_tpdb.sh

# 方式2: 直接使用 psql
PGPASSWORD='amdyes' psql -U amd -h 127.0.0.1 -p 5432 -d tpdb -f tp_data.sql

# 方式3: 使用 Django 的 loaddata（如果有 fixtures）
python manage.py loaddata tpgen_data.json --database=tpdb
```

---

### 8️⃣ 验证数据导入

```bash
python manage.py shell
```

```python
from tpgen.models import *

# 查看各表记录数
print(f"设备数: {SutDevice.objects.count()}")
print(f"OS配置数: {OsConfig.objects.count()}")
print(f"测试类型数: {TestType.objects.count()}")
print(f"测试组件数: {TestComponent.objects.count()}")
print(f"测试用例数: {TestCase.objects.count()}")
print(f"测试计划数: {TestPlan.objects.count()}")

# 查看第一条设备记录
device = SutDevice.objects.first()
if device:
    print(f"\n第一个设备: {device.hostname} - {device.gpu_model}")

# 查看第一个测试计划
plan = TestPlan.objects.first()
if plan:
    print(f"\n第一个测试计划: {plan.plan_name}")
    print(f"  设备: {plan.sut_device.hostname}")
    print(f"  OS: {plan.os_config.os_family} {plan.os_config.version}")
```

---

## 完整执行流程（复制粘贴版）

```bash
# 切换到项目目录
cd /home/xadmin

# 激活虚拟环境（如果需要）
source .venv/bin/activate

# 1. 检查配置
python manage.py check

# 2. 创建迁移（如果还没创建）
python manage.py makemigrations tpgen

# 3. 查看迁移状态
python manage.py showmigrations tpgen --database=tpdb

# 4. 应用迁移到 tpdb
python manage.py migrate tpgen --database=tpdb

# 5. 验证表已创建
PGPASSWORD='amdyes' psql -U amd -h 127.0.0.1 -p 5432 -d tpdb -c "\dt"

# 6. 导入测试数据
PGPASSWORD='amdyes' psql -U amd -h 127.0.0.1 -p 5432 -d tpdb -f tp_data.sql

# 7. 验证数据
python manage.py shell -c "
from tpgen.models import SutDevice, TestPlan
print(f'设备数: {SutDevice.objects.count()}')
print(f'测试计划数: {TestPlan.objects.count()}')
"
```

---

## 常见问题

### Q1: makemigrations 提示 "No changes detected"

**原因**: 迁移文件已经存在

**解决**: 
```bash
# 查看现有迁移
ls -la tpgen/migrations/

# 如果需要重新生成
rm tpgen/migrations/0001_initial.py
python manage.py makemigrations tpgen
```

### Q2: migrate 时提示表已存在

**原因**: 表已经在数据库中存在

**解决**:
```bash
# 方式1: 伪造迁移（标记为已应用但不执行）
python manage.py migrate tpgen --fake --database=tpdb

# 方式2: 删除表后重新迁移
PGPASSWORD='amdyes' psql -U amd -h 127.0.0.1 -p 5432 -d tpdb -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
python manage.py migrate tpgen --database=tpdb
```

### Q3: 如何回滚迁移

```bash
# 回滚到初始状态（删除所有表）
python manage.py migrate tpgen zero --database=tpdb

# 回滚到特定迁移
python manage.py migrate tpgen 0001 --database=tpdb
```

### Q4: 如何重置数据库

```bash
# 1. 删除数据库
sudo -u postgres psql -c "DROP DATABASE IF EXISTS tpdb;"

# 2. 重新创建
sudo -u postgres psql -c "CREATE DATABASE tpdb OWNER amd ENCODING 'UTF8';"

# 3. 重新迁移
python manage.py migrate tpgen --database=tpdb

# 4. 重新导入数据
PGPASSWORD='amdyes' psql -U amd -h 127.0.0.1 -p 5432 -d tpdb -f tp_data.sql
```

---

## 其他有用的命令

```bash
# 启动开发服务器
python manage.py runserver

# 创建超级用户（用于 admin）
python manage.py createsuperuser

# 导出数据
python manage.py dumpdata tpgen --database=tpdb --indent=2 > tpgen_data.json

# 导入数据
python manage.py loaddata tpgen_data.json --database=tpdb

# 清空表（保留结构）
python manage.py flush --database=tpdb
```

---

## 数据库架构确认

执行完成后，应该有以下结构：

```
PostgreSQL (127.0.0.1:5432)
│
├── xadmin (default数据库)
│   ├── sys_user
│   ├── sys_role
│   ├── sys_dept
│   └── ... (xadmin框架表)
│
└── tpdb (tpgen数据库)
    ├── sut_devices           ✓
    ├── os_configs            ✓
    ├── os_supported_kernels  ✓
    ├── test_types            ✓
    ├── test_components       ✓
    ├── test_cases            ✓
    ├── test_plans            ✓
    ├── test_plan_cases       ✓
    └── django_migrations     ✓
```

---

**创建时间**: 2025-11-11  
**适用版本**: Django 5.2.7  
**Python版本**: 3.13

