# Generated by Django 5.0.6 on 2025-01-21 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0013_attendance_record_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='punchtime',
            name='emp_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
