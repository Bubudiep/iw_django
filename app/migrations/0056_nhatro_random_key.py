# Generated by Django 5.0.2 on 2024-10-21 16:07

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0055_remove_nhatro_random_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='nhatro',
            name='random_key',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
