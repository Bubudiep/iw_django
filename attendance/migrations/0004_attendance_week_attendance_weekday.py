# Generated by Django 5.0.6 on 2025-01-20 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_punchtime_attendance_punch_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='week',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='weekday',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
