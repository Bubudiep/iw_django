# Generated by Django 5.0.6 on 2024-11-20 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0094_alter_restaurant_order_custom_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='wallpaper',
            field=models.TextField(blank=True, null=True),
        ),
    ]