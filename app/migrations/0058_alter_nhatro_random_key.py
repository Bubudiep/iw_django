# Generated by Django 5.0.2 on 2024-10-21 16:16

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0057_alter_nhatro_random_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nhatro',
            name='random_key',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
