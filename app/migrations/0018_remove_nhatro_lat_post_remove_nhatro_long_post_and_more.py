# Generated by Django 5.0.2 on 2024-10-04 08:19

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_nhatro'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nhatro',
            name='lat_post',
        ),
        migrations.RemoveField(
            model_name='nhatro',
            name='long_post',
        ),
        migrations.AddField(
            model_name='nhatro',
            name='anhDaidien',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.photos'),
        ),
        migrations.AddField(
            model_name='nhatro',
            name='chungchu',
            field=models.BooleanField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='nhatro',
            name='isActive',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AddField(
            model_name='nhatro',
            name='isBand',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AddField(
            model_name='nhatro',
            name='isLock',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.CreateModel(
            name='NhatroThongtin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tienKhac', models.FloatField(blank=True, default=0, null=True)),
                ('tienRac', models.FloatField(blank=True, default=0, null=True)),
                ('tienDien', models.FloatField(blank=True, default=0, null=True)),
                ('tienNuoctheothang', models.FloatField(blank=True, default=0, null=True)),
                ('tienNuoc', models.FloatField(blank=True, default=0, null=True)),
                ('lat_post', models.CharField(blank=True, max_length=200, null=True)),
                ('long_post', models.CharField(blank=True, max_length=200, null=True)),
                ('mota', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nhaTro', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.nhatro')),
            ],
        ),
    ]
