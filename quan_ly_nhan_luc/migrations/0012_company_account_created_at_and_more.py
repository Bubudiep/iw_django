# Generated by Django 5.0.6 on 2024-12-04 06:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0011_company_account_company_staff_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='company_account',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='company_account',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
