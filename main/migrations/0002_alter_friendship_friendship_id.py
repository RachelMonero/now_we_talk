# Generated by Django 5.1.2 on 2024-10-21 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendship',
            name='friendship_id',
            field=models.UUIDField(db_column='friendship_id', primary_key=True, serialize=False),
        ),
    ]