# Generated by Django 3.0.6 on 2021-05-27 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20210526_2014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userregistrationdetail',
            name='s_no',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='primary_key', to='users.UserRegistrationModel'),
        ),
    ]
