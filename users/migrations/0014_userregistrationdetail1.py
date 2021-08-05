# Generated by Django 3.0.6 on 2021-05-26 14:23

from django.db import migrations, models
import django.db.models.deletion
import phone_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_delete_userregistrationdetail1'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRegistrationDetail1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Gender', models.CharField(max_length=10)),
                ('phone_number', phone_field.models.PhoneField(max_length=31)),
                ('Address1', models.CharField(max_length=200)),
                ('Address2', models.CharField(max_length=200)),
                ('City', models.CharField(max_length=20)),
                ('date_joined', models.DateTimeField(default=None)),
                ('modified_date', models.DateTimeField(default=None)),
                ('s_no', models.ForeignKey(default=True, on_delete=django.db.models.deletion.CASCADE, to='users.UserRegistrationModel')),
            ],
        ),
    ]
