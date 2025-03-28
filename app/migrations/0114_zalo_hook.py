# Generated by Django 5.1.3 on 2024-12-04 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0113_restaurant_order_items_is_rejected"),
    ]

    operations = [
        migrations.CreateModel(
            name="Zalo_hook",
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
                ("data", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
