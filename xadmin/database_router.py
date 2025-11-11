"""
数据库路由器 - 将 tpgen 应用路由到 tpdb 数据库
其他应用使用 xadmin 数据库
"""


class TpgenDatabaseRouter:
    """
    路由器：将 tpgen 应用的所有数据库操作路由到 tpdb 数据库
    """

    # tpgen 应用使用的数据库标识
    tpgen_db = "tpdb"
    # tpgen 应用名称
    tpgen_app = "tpgen"

    def db_for_read(self, model, **hints):
        """
        读操作路由
        """
        if model._meta.app_label == self.tpgen_app:
            return self.tpgen_db
        return None

    def db_for_write(self, model, **hints):
        """
        写操作路由
        """
        if model._meta.app_label == self.tpgen_app:
            return self.tpgen_db
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        允许关系：同一数据库内的关系
        """
        db_set = {self.tpgen_db, "default"}
        if obj1._meta.app_label == self.tpgen_app or obj2._meta.app_label == self.tpgen_app:
            # 如果任一对象来自 tpgen，检查是否都在同一数据库
            return obj1._meta.app_label == obj2._meta.app_label
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        迁移权限：tpgen 只迁移到 tpdb，其他应用只迁移到 default
        """
        if app_label == self.tpgen_app:
            # tpgen 应用只能迁移到 tpdb
            return db == self.tpgen_db
        # 其他应用只能迁移到 default
        return db == "default"

