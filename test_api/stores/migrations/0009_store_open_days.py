# Generated by Django 5.1.6 on 2025-02-18 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0008_rename_state_store_state_abbrv'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='open_days',
            field=models.JSONField(default=list),
        ),
    ]
