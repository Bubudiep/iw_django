# Generated by Django 5.0.6 on 2024-12-03 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0003_company_department_company_possition_company_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='company_department',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='company_possition',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
