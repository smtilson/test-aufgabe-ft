# Generated by Django 5.1.6 on 2025-02-19 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0010_day_remove_store_open_days_store_open_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='day',
            field=models.CharField(choices=[('Mo', 'Montag'), ('Di', 'Dienstag'), ('Mi', 'Mittwoch'), ('Do', 'Donnerstag'), ('Fr', 'Freitag'), ('Sa', 'Samstag'), ('So', 'Sonntag')], max_length=2, unique=True),
        ),
    ]
