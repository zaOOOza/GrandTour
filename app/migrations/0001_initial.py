# Generated by Django 4.1.1 on 2022-09-29 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_route', models.IntegerField()),
                ('event_admin', models.IntegerField()),
                ('approved_user', models.JSONField()),
                ('pending_user', models.JSONField()),
                ('start_date', models.DateField()),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Places',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_point', models.IntegerField()),
                ('stopping_point', models.JSONField()),
                ('destination', models.IntegerField()),
                ('country', models.CharField(max_length=50)),
                ('location', models.CharField(max_length=120)),
                ('description', models.TextField()),
                ('route_type', models.CharField(choices=[('car', 'car'), ('foot', 'foot'), ('bicycle', 'bicycle')], default='foot', max_length=10)),
                ('duration', models.IntegerField()),
            ],
        ),
    ]
