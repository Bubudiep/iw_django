# Generated by Django 5.0.6 on 2024-12-12 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0021_company_customer_staffs'),
    ]

    operations = [
        migrations.AddField(
            model_name='company_customer',
            name='website',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]