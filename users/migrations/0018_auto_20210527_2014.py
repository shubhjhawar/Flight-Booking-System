# Generated by Django 3.0.6 on 2021-05-27 14:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20210527_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userregistrationdetail',
            name='s_no',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.UserRegistrationModel'),
        ),
    ]
