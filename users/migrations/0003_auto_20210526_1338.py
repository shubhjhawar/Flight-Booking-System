# Generated by Django 3.0.6 on 2021-05-26 08:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210526_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='admin',
        ),
        migrations.RemoveField(
            model_name='account',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='account',
            name='user',
        ),
    ]