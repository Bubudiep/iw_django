# Generated by Django 5.0.6 on 2025-01-08 00:59

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0039_delete_phanquyen'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('min_company_level', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Permission',
                'verbose_name_plural': 'Permissions',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='CompanyPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('assigned_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('applicable_departments', models.ManyToManyField(blank=True, related_name='company_permissions', to='quan_ly_nhan_luc.company_department')),
                ('applicable_positions', models.ManyToManyField(blank=True, related_name='company_permissions', to='quan_ly_nhan_luc.company_possition')),
                ('applicable_staff', models.ManyToManyField(blank=True, related_name='company_permissions', to='quan_ly_nhan_luc.company_staff')),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quan_ly_nhan_luc.company_staff')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='quan_ly_nhan_luc.company')),
                ('excluded_staff', models.ManyToManyField(blank=True, related_name='excluded_permissions', to='quan_ly_nhan_luc.company_staff')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quan_ly_nhan_luc.permission')),
            ],
            options={
                'verbose_name': 'Company Permission',
                'verbose_name_plural': 'Company Permissions',
                'unique_together': {('company', 'permission')},
            },
        ),
    ]
