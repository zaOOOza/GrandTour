# Generated by Django 4.1.1 on 2022-09-30 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='route_type',
            field=models.CharField(choices=[('car', 'car'), ('foot', 'foot'), ('bicycle', 'bicycle')], default='foot', max_length=20),
        ),
    ]