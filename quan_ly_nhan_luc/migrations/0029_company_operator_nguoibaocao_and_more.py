# Generated by Django 5.0.6 on 2024-12-20 09:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0028_company_operator_nganhang_company_operator_trangthai'),
    ]

    operations = [
        migrations.AddField(
            model_name='company_operator',
            name='nguoibaocao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='companyOP_nguoibaocao', to='quan_ly_nhan_luc.company_staff'),
        ),
        migrations.AlterField(
            model_name='company_operator',
            name='nguoituyen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='companyOP_nguoituyen', to='quan_ly_nhan_luc.company_staff'),
        ),
    ]