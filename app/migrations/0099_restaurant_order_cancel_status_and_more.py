# Generated by Django 5.0.6 on 2024-11-21 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0098_alter_restaurant_order_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant_order',
            name='cancel_status',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='restaurant_order',
            name='status',
            field=models.CharField(choices=[('CREATED', 'Đã tạo'), ('RECEIVED', 'Đã nhận'), ('SHIPPING', 'Đang ship'), ('DELIVERED', 'Đã giao'), ('PADING', 'Đang thanh toán'), ('COMPLETE', 'Hoàn thành'), ('NOT', 'Không nhận'), ('CANCEL', 'Người dùng hủy')], default='CREATED', max_length=20),
        ),
    ]