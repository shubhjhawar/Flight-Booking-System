# Generated by Django 3.0.6 on 2021-06-17 13:54

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_merge_20210617_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='userregistrationmodel',
            name='code',
            field=models.CharField(default=users.models.generate_activation_code, max_length=6),
        ),
    ]
