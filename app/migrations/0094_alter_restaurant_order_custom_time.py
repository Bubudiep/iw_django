# Generated by Django 5.0.6 on 2024-11-19 06:17

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0093_lenmonalert'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant_order',
            name='custom_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
