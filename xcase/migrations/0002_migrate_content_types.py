# Migration to update ContentType records from xdb to xcase

from django.db import migrations


def migrate_content_types_forward(apps, schema_editor):
    """
    将 CaseMetadata, CaseTag, CaseOption 的 ContentType 从 xdb 更新到 xcase
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # 更新模型的 app_label
    models_to_migrate = ['casemetadata', 'casetag', 'caseoption']
    
    for model_name in models_to_migrate:
        try:
            ct = ContentType.objects.get(app_label='xdb', model=model_name)
            ct.app_label = 'xcase'
            ct.save()
            print(f"Migrated ContentType: xdb.{model_name} -> xcase.{model_name}")
        except ContentType.DoesNotExist:
            print(f"ContentType not found: xdb.{model_name} (may not exist yet)")


def migrate_content_types_backward(apps, schema_editor):
    """
    回滚：将 ContentType 从 xcase 还原到 xdb
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    models_to_migrate = ['casemetadata', 'casetag', 'caseoption']
    
    for model_name in models_to_migrate:
        try:
            ct = ContentType.objects.get(app_label='xcase', model=model_name)
            ct.app_label = 'xdb'
            ct.save()
            print(f"Rolled back ContentType: xcase.{model_name} -> xdb.{model_name}")
        except ContentType.DoesNotExist:
            print(f"ContentType not found: xcase.{model_name}")


class Migration(migrations.Migration):

    dependencies = [
        ('xcase', '0001_initial'),
        ('contenttypes', '__latest__'),
    ]

    operations = [
        migrations.RunPython(
            migrate_content_types_forward,
            reverse_code=migrate_content_types_backward,
        ),
    ]

