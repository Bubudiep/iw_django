# Generated by Django 5.0.6 on 2024-12-11 03:43

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0015_company_staff_profile_bank_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='company_staff_history_action',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='company_staff_history_function',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='company_staff_history',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_action', models.GenericIPAddressField(blank=True, null=True)),
                ('old_data', models.JSONField(blank=True, null=True)),
                ('new_data', models.JSONField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('isHidden', models.BooleanField(blank=True, default=False, null=True)),
                ('isSended', models.BooleanField(blank=True, default=False, null=True)),
                ('isReceived', models.BooleanField(blank=True, default=False, null=True)),
                ('isReaded', models.BooleanField(blank=True, default=False, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quan_ly_nhan_luc.company_staff')),
                ('action', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quan_ly_nhan_luc.company_staff_history_action')),
                ('function', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quan_ly_nhan_luc.company_staff_history_function')),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
