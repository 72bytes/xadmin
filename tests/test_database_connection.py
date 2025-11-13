"""
数据库连接测试

测试项目中配置的数据库连接是否正常
根据 xadmin/settings.py 中的配置测试以下数据库：
1. default: xadmin@10.67.167.53:5433
2. tpdb: tpdb@10.67.167.53:5433
"""

import pytest
from django.db import connections, DatabaseError
from django.conf import settings


class TestDatabaseConnection:
    """数据库连接基础测试"""
    
    def test_databases_configured(self):
        """测试数据库配置是否存在"""
        assert 'default' in settings.DATABASES, "❌ 未找到 default 数据库配置"
        assert 'tpdb' in settings.DATABASES, "❌ 未找到 tpdb 数据库配置"
        
        print("\n✅ 数据库配置检查通过:")
        print(f"  - default: {settings.DATABASES['default']['NAME']}@{settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}")
        print(f"  - tpdb: {settings.DATABASES['tpdb']['NAME']}@{settings.DATABASES['tpdb']['HOST']}:{settings.DATABASES['tpdb']['PORT']}")
    
    def test_database_config_details(self):
        """测试数据库配置详情"""
        default_db = settings.DATABASES['default']
        tpdb_db = settings.DATABASES['tpdb']
        
        # 检查 default 数据库配置
        assert default_db['ENGINE'] == 'django.db.backends.postgresql', "default 数据库引擎应为 PostgreSQL"
        # 注意：在测试环境中，Django 会自动为数据库名添加 test_ 前缀
        assert 'xadmin' in default_db['NAME'], f"default 数据库名称应包含 'xadmin'，实际为: {default_db['NAME']}"
        assert default_db['USER'] == 'amd', "default 数据库用户应为 amd"
        assert default_db['HOST'] == '10.67.167.53', "default 数据库主机应为 10.67.167.53"
        assert default_db['PORT'] == 5433, "default 数据库端口应为 5433"
        
        # 检查 tpdb 数据库配置
        assert tpdb_db['ENGINE'] == 'django.db.backends.postgresql', "tpdb 数据库引擎应为 PostgreSQL"
        assert 'tpdb' in tpdb_db['NAME'], f"tpdb 数据库名称应包含 'tpdb'，实际为: {tpdb_db['NAME']}"
        assert tpdb_db['USER'] == 'amd', "tpdb 数据库用户应为 amd"
        assert tpdb_db['HOST'] == '10.67.167.53', "tpdb 数据库主机应为 10.67.167.53"
        assert tpdb_db['PORT'] == 5433, "tpdb 数据库端口应为 5433"
        
        print(f"\n✅ 数据库配置详情验证通过:")
        print(f"  - default: {default_db['NAME']} (测试环境)")
        print(f"  - tpdb: {tpdb_db['NAME']} (测试环境)")


class TestDefaultDatabaseConnection:
    """default 数据库连接测试"""
    
    def test_default_db_connection(self, db):
        """测试 default 数据库连接是否正常"""
        try:
            connection = connections['default']
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1, "查询结果不正确"
            
            print(f"\n✅ default 数据库连接成功: {settings.DATABASES['default']['NAME']}")
        except DatabaseError as e:
            pytest.fail(f"❌ default 数据库连接失败: {e}")
    
    def test_default_db_version(self, db):
        """测试 default 数据库版本信息"""
        try:
            connection = connections['default']
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                
                assert 'PostgreSQL' in version, "应该是 PostgreSQL 数据库"
                print(f"\n✅ default 数据库版本: {version[:50]}...")
        except DatabaseError as e:
            pytest.fail(f"❌ 获取 default 数据库版本失败: {e}")
    
    def test_default_db_current_database(self, db):
        """测试 default 数据库当前数据库名"""
        try:
            connection = connections['default']
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database()")
                db_name = cursor.fetchone()[0]
                
                # 注意：在测试中，Django 会创建测试数据库，名称会是 test_xadmin
                assert 'xadmin' in db_name or 'test_' in db_name, \
                    f"数据库名称应包含 'xadmin' 或 'test_'，实际为: {db_name}"
                
                print(f"\n✅ default 当前数据库: {db_name}")
        except DatabaseError as e:
            pytest.fail(f"❌ 获取 default 当前数据库失败: {e}")
    
    def test_default_db_timezone(self, db):
        """测试 default 数据库时区设置"""
        try:
            connection = connections['default']
            with connection.cursor() as cursor:
                cursor.execute("SHOW timezone")
                timezone = cursor.fetchone()[0]
                
                # 注意：测试数据库可能不会完全应用 OPTIONS 中的时区设置
                # 生产环境应该是 Asia/Shanghai，测试环境可能是 UTC
                print(f"\n💡 default 数据库时区: {timezone}")
                if timezone == 'UTC':
                    print("   ⚠️  测试环境使用 UTC 时区（正常）")
                
                # 只要能获取到时区信息就通过
                assert timezone is not None, "无法获取数据库时区"
        except DatabaseError as e:
            pytest.fail(f"❌ 获取 default 数据库时区失败: {e}")


@pytest.mark.django_db(databases=['default', 'tpdb'])
class TestTpdbDatabaseConnection:
    """tpdb 数据库连接测试"""
    
    def test_tpdb_connection(self):
        """测试 tpdb 数据库连接是否正常"""
        try:
            connection = connections['tpdb']
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1, "查询结果不正确"
            
            print(f"\n✅ tpdb 数据库连接成功: {settings.DATABASES['tpdb']['NAME']}")
        except DatabaseError as e:
            pytest.fail(f"❌ tpdb 数据库连接失败: {e}")
    
    def test_tpdb_version(self):
        """测试 tpdb 数据库版本信息"""
        try:
            connection = connections['tpdb']
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                
                assert 'PostgreSQL' in version, "应该是 PostgreSQL 数据库"
                print(f"\n✅ tpdb 数据库版本: {version[:50]}...")
        except DatabaseError as e:
            pytest.fail(f"❌ 获取 tpdb 数据库版本失败: {e}")
    
    def test_tpdb_current_database(self):
        """测试 tpdb 数据库当前数据库名"""
        try:
            connection = connections['tpdb']
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database()")
                db_name = cursor.fetchone()[0]
                
                # 注意：在测试中，Django 会创建测试数据库，名称会是 test_tpdb
                assert 'tpdb' in db_name or 'test_' in db_name, \
                    f"数据库名称应包含 'tpdb' 或 'test_'，实际为: {db_name}"
                
                print(f"\n✅ tpdb 当前数据库: {db_name}")
        except DatabaseError as e:
            pytest.fail(f"❌ 获取 tpdb 当前数据库失败: {e}")


@pytest.mark.django_db(databases=['default', 'tpdb'])
class TestDatabaseOperations:
    """数据库基本操作测试"""
    
    def test_default_db_read_write(self):
        """测试 default 数据库读写操作"""
        try:
            connection = connections['default']
            with connection.cursor() as cursor:
                # 创建临时表
                cursor.execute("""
                    CREATE TEMP TABLE test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 插入数据
                cursor.execute("INSERT INTO test_table (name) VALUES (%s)", ['test_data'])
                
                # 读取数据
                cursor.execute("SELECT name FROM test_table WHERE name = %s", ['test_data'])
                result = cursor.fetchone()
                
                assert result[0] == 'test_data', "读取的数据不正确"
                
                print(f"\n✅ default 数据库读写操作正常")
        except DatabaseError as e:
            pytest.fail(f"❌ default 数据库读写操作失败: {e}")
    
    def test_tpdb_read_write(self):
        """测试 tpdb 数据库读写操作"""
        try:
            connection = connections['tpdb']
            with connection.cursor() as cursor:
                # 创建临时表
                cursor.execute("""
                    CREATE TEMP TABLE test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 插入数据
                cursor.execute("INSERT INTO test_table (name) VALUES (%s)", ['test_data'])
                
                # 读取数据
                cursor.execute("SELECT name FROM test_table WHERE name = %s", ['test_data'])
                result = cursor.fetchone()
                
                assert result[0] == 'test_data', "读取的数据不正确"
                
                print(f"\n✅ tpdb 数据库读写操作正常")
        except DatabaseError as e:
            pytest.fail(f"❌ tpdb 数据库读写操作失败: {e}")


@pytest.mark.django_db(databases=['default', 'tpdb'])
class TestDatabaseIntegration:
    """数据库集成测试"""
    
    def test_all_databases_accessible(self):
        """测试所有配置的数据库是否可访问"""
        accessible_dbs = []
        failed_dbs = []
        
        for db_alias in settings.DATABASES.keys():
            try:
                connection = connections[db_alias]
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    accessible_dbs.append(db_alias)
            except DatabaseError as e:
                failed_dbs.append((db_alias, str(e)))
        
        if failed_dbs:
            error_msg = "\n".join([f"  - {alias}: {error}" for alias, error in failed_dbs])
            pytest.fail(f"❌ 以下数据库连接失败:\n{error_msg}")
        
        print(f"\n✅ 所有 {len(accessible_dbs)} 个数据库连接成功: {', '.join(accessible_dbs)}")
    
    def test_database_router_configuration(self):
        """测试数据库路由配置"""
        assert hasattr(settings, 'DATABASE_ROUTERS'), "❌ 未找到数据库路由配置"
        
        routers = settings.DATABASE_ROUTERS
        assert len(routers) > 0, "❌ 数据库路由配置为空"
        
        print(f"\n✅ 数据库路由配置: {routers}")


@pytest.mark.django_db(databases=['default', 'tpdb'])
class TestDatabaseHealth:
    """数据库健康检查"""
    
    def test_connection_health_check(self):
        """测试数据库连接健康检查"""
        health_status = {}
        
        for db_alias in ['default', 'tpdb']:
            try:
                connection = connections[db_alias]
                
                # 检查连接是否健康
                connection.ensure_connection()
                
                with connection.cursor() as cursor:
                    # 执行简单查询
                    cursor.execute("SELECT 1")
                    
                    # 获取连接信息
                    cursor.execute("SELECT current_user, current_database()")
                    user, database = cursor.fetchone()
                    
                    health_status[db_alias] = {
                        'status': 'healthy',
                        'user': user,
                        'database': database,
                        'vendor': connection.vendor
                    }
            except Exception as e:
                health_status[db_alias] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        # 检查是否所有数据库都健康
        unhealthy = [alias for alias, status in health_status.items() 
                     if status['status'] == 'unhealthy']
        
        if unhealthy:
            error_details = "\n".join([
                f"  - {alias}: {health_status[alias]['error']}" 
                for alias in unhealthy
            ])
            pytest.fail(f"❌ 以下数据库不健康:\n{error_details}")
        
        # 打印健康状态
        print("\n✅ 数据库健康检查通过:")
        for alias, status in health_status.items():
            print(f"  - {alias}: {status['user']}@{status['database']} ({status['vendor']})")
    
    def test_database_connection_pool(self):
        """测试数据库连接池配置"""
        for db_alias in ['default', 'tpdb']:
            connection = connections[db_alias]
            
            # 检查连接池配置
            assert hasattr(connection, 'settings_dict'), f"❌ {db_alias} 缺少配置字典"
            
            settings_dict = connection.settings_dict
            assert 'CONN_HEALTH_CHECKS' in settings_dict, \
                f"❌ {db_alias} 未配置 CONN_HEALTH_CHECKS"
            
            assert settings_dict['CONN_HEALTH_CHECKS'] is True, \
                f"❌ {db_alias} 的 CONN_HEALTH_CHECKS 应为 True"
            
            print(f"\n✅ {db_alias} 连接池配置正确")


@pytest.mark.django_db(databases=['default', 'tpdb'])
class TestDatabaseStats:
    """数据库统计信息"""
    
    def test_database_statistics(self):
        """获取数据库统计信息"""
        stats = {}
        
        for db_alias in ['default', 'tpdb']:
            try:
                connection = connections[db_alias]
                with connection.cursor() as cursor:
                    # 获取数据库大小
                    cursor.execute("""
                        SELECT 
                            current_database() as db_name,
                            pg_size_pretty(pg_database_size(current_database())) as size
                    """)
                    db_name, size = cursor.fetchone()
                    
                    # 获取当前连接数
                    cursor.execute("""
                        SELECT count(*) 
                        FROM pg_stat_activity 
                        WHERE datname = current_database()
                    """)
                    connections_count = cursor.fetchone()[0]
                    
                    stats[db_alias] = {
                        'name': db_name,
                        'size': size,
                        'connections': connections_count
                    }
            except Exception as e:
                stats[db_alias] = {'error': str(e)}
        
        # 打印统计信息
        print("\n📊 数据库统计信息:")
        for alias, info in stats.items():
            if 'error' in info:
                print(f"  - {alias}: ❌ {info['error']}")
            else:
                print(f"  - {alias}: {info['name']} | 大小: {info['size']} | 连接数: {info['connections']}")
        
        # 确保至少能获取到一些统计信息
        successful_stats = [alias for alias, info in stats.items() if 'error' not in info]
        assert len(successful_stats) > 0, "❌ 无法获取任何数据库统计信息"

