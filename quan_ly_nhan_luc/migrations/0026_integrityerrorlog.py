# Generated by Django 5.1.3 on 2024-12-19 10:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "quan_ly_nhan_luc",
            "0025_alter_company_options_alter_company_account_options_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="IntegrityErrorLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("error_message", models.TextField()),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                ("endpoint", models.CharField(blank=True, max_length=255, null=True)),
                ("payload", models.JSONField(blank=True, null=True)),
            ],
        ),
    ]