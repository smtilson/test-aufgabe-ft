# Generated by Django 5.1.6 on 2025-02-19 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0015_rename_managers_store_manager_ids_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='closing_time',
            field=models.TimeField(default='17:00:00'),
        ),
        migrations.AlterField(
            model_name='store',
            name='opening_time',
            field=models.TimeField(default='07:00:00'),
        ),
    ]
