# Generated by Django 5.0.2 on 2024-10-18 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0040_phong_dieuhoa_phong_nonglanh_phong_wifi_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nguoitro',
            name='tiencoc',
        ),
        migrations.AddField(
            model_name='lichsunguoitro',
            name='tiencoc',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
