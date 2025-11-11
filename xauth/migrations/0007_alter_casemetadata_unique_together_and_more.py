# Migration to remove Case models from xdb state (they are now in xcase)
# This only removes them from migration state, not from the database

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xauth', '0006_update_app_labels'),
    ]

    operations = [
        # Use SeparateDatabaseAndState to only update migration state
        # without affecting the database tables (they are now managed by xcase)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterUniqueTogether(
                    name='casemetadata',
                    unique_together=None,
                ),
                migrations.RemoveField(
                    model_name='caseoption',
                    name='metadata',
                ),
                migrations.AlterUniqueTogether(
                    name='caseoption',
                    unique_together=None,
                ),
                migrations.DeleteModel(
                    name='CaseTag',
                ),
                migrations.DeleteModel(
                    name='CaseMetadata',
                ),
                migrations.DeleteModel(
                    name='CaseOption',
                ),
            ],
            # No database operations needed - tables are managed by xcase
            database_operations=[],
        ),
    ]
