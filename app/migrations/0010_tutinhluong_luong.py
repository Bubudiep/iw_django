# Generated by Django 5.0.6 on 2024-09-26 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_album_is_public_photos_is_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutinhluong',
            name='luong',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
