# Generated by Django 5.0.6 on 2024-11-07 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0068_fixed_link_restaurant_qr_login_restaurant_menu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fixed_link',
            name='name',
        ),
        migrations.RemoveField(
            model_name='fixed_link',
            name='option',
        ),
        migrations.AddField(
            model_name='fixed_link',
            name='app',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='fixed_link',
            name='platform',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
