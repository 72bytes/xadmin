# Generated migration to clean up test_plan table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xauth', '0004_add_case_browser_and_metadata'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS test_plan CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

