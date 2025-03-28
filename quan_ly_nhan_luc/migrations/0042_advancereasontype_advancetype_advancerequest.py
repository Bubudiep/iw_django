# Generated by Django 5.0.6 on 2025-02-27 04:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quan_ly_nhan_luc', '0041_operator_history_nguoituyen_operator_history_reason'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvanceReasonType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typename', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AdvanceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typecode', models.CharField(max_length=100, unique=True)),
                ('need_operator', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AdvanceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('comment', models.TextField()),
                ('status', models.CharField(choices=[('cancel', 'Hủy bỏ'), ('pending', 'Chờ duyệt'), ('approved', 'Đã duyệt'), ('rejected', 'Từ chối')], default='pending', max_length=10)),
                ('payment_status', models.CharField(choices=[('unpaid', 'Chưa thanh toán'), ('paid', 'Đã thanh toán')], default='unpaid', max_length=10)),
                ('retrieve_status', models.CharField(choices=[('not_retrieved', 'Chưa thu hồi'), ('retrieved', 'Đã thu hồi')], default='not_retrieved', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='advance_approver', to='quan_ly_nhan_luc.company_staff')),
                ('operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='advance_operator', to='quan_ly_nhan_luc.company_operator')),
                ('reason', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='advance_reason', to='quan_ly_nhan_luc.advancereasontype')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advance_requests', to='quan_ly_nhan_luc.company_staff')),
                ('requesttype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advance_type', to='quan_ly_nhan_luc.advancetype')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
