# Generated by Django 5.0.2 on 2024-10-15 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_nguoitro_tiencoc'),
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
