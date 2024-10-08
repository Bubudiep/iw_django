# Generated by Django 5.0.2 on 2024-10-04 07:12

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_tuchamcongtay_ca_tuchamcongtay_kieungay'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Nhatro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tenTro', models.CharField(blank=True, max_length=200, null=True)),
                ('giaphongThapnhat', models.FloatField(blank=True, default=0, null=True)),
                ('giaphongCaonhat', models.FloatField(blank=True, default=0, null=True)),
                ('dieuhoa', models.BooleanField(blank=True, default=0, null=True)),
                ('nonglanh', models.BooleanField(blank=True, default=0, null=True)),
                ('wifi', models.BooleanField(blank=True, default=0, null=True)),
                ('hotline', models.CharField(blank=True, max_length=200, null=True)),
                ('diachi', models.CharField(blank=True, max_length=200, null=True)),
                ('lat_post', models.CharField(blank=True, max_length=200, null=True)),
                ('long_post', models.CharField(blank=True, max_length=200, null=True)),
                ('mota', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
