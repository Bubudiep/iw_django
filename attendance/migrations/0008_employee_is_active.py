# Generated by Django 5.0.6 on 2025-01-20 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0007_profile_emp_id_alter_employee_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
