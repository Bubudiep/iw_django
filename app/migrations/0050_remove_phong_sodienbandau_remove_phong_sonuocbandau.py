# Generated by Django 5.0.2 on 2024-10-20 02:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0049_phong_sodienbandau_phong_sonuocbandau'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='phong',
            name='sodienbandau',
        ),
        migrations.RemoveField(
            model_name='phong',
            name='sonuocbandau',
        ),
    ]
