# Generated by Django 3.0.6 on 2021-05-26 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20210526_1553'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userregistrationdetail',
            old_name='last_login',
            new_name='modified_date',
        ),
        migrations.RemoveField(
            model_name='userregistrationdetail',
            name='username',
        ),
        migrations.AddField(
            model_name='userregistrationdetail',
            name='s_no',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, to='users.UserRegistrationModel'),
        ),
        migrations.AddField(
            model_name='userregistrationmodel',
            name='role',
            field=models.CharField(choices=[('a', 'user'), ('i', 'admin')], default='user', max_length=20),
        ),
        migrations.AlterField(
            model_name='userregistrationmodel',
            name='is_active',
            field=models.CharField(choices=[('a', 'active'), ('i', 'inactive')], default='inactive', max_length=20),
        ),
    ]
