# Generated by Django 5.0.6 on 2024-12-20 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0027_company_operator_gioi_tinh_company_operator_quequan'),
    ]

    operations = [
        migrations.AddField(
            model_name='company_operator',
            name='nganhang',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='company_operator',
            name='trangthai',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]