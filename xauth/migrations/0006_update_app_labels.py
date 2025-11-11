# Migration to update app_label in ContentType table after app renaming

from django.db import migrations


def update_app_labels_forward(apps, schema_editor):
    """
    更新 ContentType 中的 app_label:
    xadmin_auth -> xauth
    xadmin_db -> xdb
    xadmin_utils -> xutils
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # 更新 xadmin_auth -> xauth
    auth_types = ContentType.objects.filter(app_label='xadmin_auth')
    count = auth_types.count()
    auth_types.update(app_label='xauth')
    print(f"Updated {count} ContentType records: xadmin_auth -> xauth")
    
    # 更新 xadmin_db -> xdb
    db_types = ContentType.objects.filter(app_label='xadmin_db')
    count = db_types.count()
    db_types.update(app_label='xauth')
    print(f"Updated {count} ContentType records: xadmin_db -> xdb")
    
    # 更新 xadmin_utils -> xutils
    utils_types = ContentType.objects.filter(app_label='xadmin_utils')
    count = utils_types.count()
    utils_types.update(app_label='xutils')
    print(f"Updated {count} ContentType records: xadmin_utils -> xutils")


def update_app_labels_backward(apps, schema_editor):
    """
    回滚：将 app_label 还原为旧名称
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # 回滚 xauth -> xadmin_auth
    auth_types = ContentType.objects.filter(app_label='xauth')
    count = auth_types.count()
    auth_types.update(app_label='xadmin_auth')
    print(f"Rolled back {count} ContentType records: xauth -> xadmin_auth")
    
    # 回滚 xdb -> xadmin_db
    db_types = ContentType.objects.filter(app_label='xauth')
    count = db_types.count()
    db_types.update(app_label='xadmin_db')
    print(f"Rolled back {count} ContentType records: xdb -> xadmin_db")
    
    # 回滚 xutils -> xadmin_utils
    utils_types = ContentType.objects.filter(app_label='xutils')
    count = utils_types.count()
    utils_types.update(app_label='xadmin_utils')
    print(f"Rolled back {count} ContentType records: xutils -> xadmin_utils")


class Migration(migrations.Migration):

    dependencies = [
        ('xauth', '0005_remove_testplan_table'),
        ('contenttypes', '__latest__'),
    ]

    operations = [
        migrations.RunPython(
            update_app_labels_forward,
            reverse_code=update_app_labels_backward,
        ),
    ]

