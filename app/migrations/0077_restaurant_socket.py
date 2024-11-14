# Generated by Django 5.1.3 on 2024-11-09 18:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0076_restaurant_oder_online_restaurant_takeaway_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Restaurant_socket",
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
                ("name", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "QRKey",
                    models.CharField(
                        blank=True,
                        editable=False,
                        max_length=32,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "restaurant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.restaurant",
                    ),
                ),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
    ]