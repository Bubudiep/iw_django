# Generated by Django 5.0.6 on 2024-09-16 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_album_photos_album'),
    ]

    operations = [
        migrations.AddField(
            model_name='photos',
            name='data_mini',
            field=models.TextField(blank=True, null=True),
        ),
    ]
