# Generated by Django 5.0.6 on 2024-12-03 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='addressDetails',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='companyCode',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
