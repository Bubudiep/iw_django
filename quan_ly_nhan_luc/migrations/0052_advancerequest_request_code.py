# Generated by Django 5.0.6 on 2025-03-07 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0051_alter_advancerequest_payment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancerequest',
            name='request_code',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]
