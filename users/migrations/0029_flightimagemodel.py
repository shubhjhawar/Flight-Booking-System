# Generated by Django 3.0.6 on 2021-06-08 23:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_auto_20210608_1959'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlightImageModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('flight_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.FlightModel')),
            ],
        ),
    ]
