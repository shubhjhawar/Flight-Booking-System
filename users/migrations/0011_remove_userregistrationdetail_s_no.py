# Generated by Django 3.0.6 on 2021-05-26 13:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_userregistrationdetail_s_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userregistrationdetail',
            name='s_no',
        ),
    ]
