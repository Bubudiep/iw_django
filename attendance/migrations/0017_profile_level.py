# Generated by Django 5.0.6 on 2025-01-22 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0016_alter_attendance_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='level',
            field=models.IntegerField(default=1),
        ),
    ]
