-- XAdmin 初始化数据库脚本
-- 自动创建 tpdb 数据库

-- 创建 tpdb 数据库（如果不存在）
SELECT 'CREATE DATABASE tpdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'tpdb')\gexec

-- 设置时区
SET timezone = 'Asia/Shanghai';

-- 输出初始化完成信息
\echo 'Database initialization completed.'







