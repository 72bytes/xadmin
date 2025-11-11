# Generated migration for XCase models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # 由于表已经在数据库中存在（由 xdb 创建），
        # 我们不创建表，只声明模型状态
        migrations.CreateModel(
            name='CaseMetadata',
            fields=[
                ('id', models.BigAutoField(db_comment='ID', primary_key=True, serialize=False)),
                ('casespace', models.CharField(db_comment='Casespace名称', db_index=True, max_length=255)),
                ('case_name', models.CharField(db_comment='Case名称', db_index=True, max_length=255)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_comment='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, db_comment='更新时间')),
            ],
            options={
                'db_table': 'case_metadata',
                'db_table_comment': 'Case元数据表',
                'ordering': ['-update_time'],
            },
        ),
        migrations.CreateModel(
            name='CaseTag',
            fields=[
                ('id', models.BigAutoField(db_comment='ID', primary_key=True, serialize=False)),
                ('tag', models.CharField(db_comment='标签名称', db_index=True, max_length=100)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_comment='创建时间')),
                ('metadata', models.ForeignKey(db_comment='关联的case元数据', on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='xcase.casemetadata')),
            ],
            options={
                'db_table': 'case_tag',
                'db_table_comment': 'Case标签表',
                'ordering': ['tag'],
            },
        ),
        migrations.CreateModel(
            name='CaseOption',
            fields=[
                ('id', models.BigAutoField(db_comment='ID', primary_key=True, serialize=False)),
                ('key', models.CharField(db_comment='选项键', db_index=True, max_length=100)),
                ('value', models.CharField(db_comment='选项值', max_length=500)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_comment='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, db_comment='更新时间')),
                ('metadata', models.ForeignKey(db_comment='关联的case元数据', on_delete=django.db.models.deletion.CASCADE, related_name='options', to='xcase.casemetadata')),
            ],
            options={
                'db_table': 'case_option',
                'db_table_comment': 'Case选项表',
                'ordering': ['key'],
            },
        ),
        migrations.AddIndex(
            model_name='casemetadata',
            index=models.Index(fields=['casespace', 'case_name'], name='case_metada_casesp_8b8e92_idx'),
        ),
        migrations.AddIndex(
            model_name='casemetadata',
            index=models.Index(fields=['create_time'], name='case_metada_create__3f3e5e_idx'),
        ),
        migrations.AddIndex(
            model_name='casemetadata',
            index=models.Index(fields=['update_time'], name='case_metada_update__3ae091_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='casemetadata',
            unique_together={('casespace', 'case_name')},
        ),
        migrations.AddIndex(
            model_name='casetag',
            index=models.Index(fields=['tag'], name='case_tag_tag_5c1f0f_idx'),
        ),
        migrations.AddIndex(
            model_name='casetag',
            index=models.Index(fields=['metadata', 'tag'], name='case_tag_metadat_44f583_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='casetag',
            unique_together={('metadata', 'tag')},
        ),
        migrations.AddIndex(
            model_name='caseoption',
            index=models.Index(fields=['key'], name='case_option_key_9c7831_idx'),
        ),
        migrations.AddIndex(
            model_name='caseoption',
            index=models.Index(fields=['metadata', 'key'], name='case_option_metadat_3e1ea7_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='caseoption',
            unique_together={('metadata', 'key')},
        ),
    ]

