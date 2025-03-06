# Generated by Django 5.0.6 on 2025-03-06 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0048_alter_advancerequest_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancerequest',
            name='hinhthucThanhtoan',
            field=models.CharField(choices=[('bank', 'Chuyển khoản'), ('money', 'Tiền mặt')], default='bank', max_length=10),
        ),
        migrations.AddField(
            model_name='advancerequest',
            name='khacCtk',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='advancerequest',
            name='khacNganhang',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='advancerequest',
            name='khacStk',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='advancerequest',
            name='nguoiThuhuong',
            field=models.CharField(choices=[('other', 'Chuyển khoản'), ('money', 'Tiền mặt')], default='pending', max_length=10),
        ),
    ]
