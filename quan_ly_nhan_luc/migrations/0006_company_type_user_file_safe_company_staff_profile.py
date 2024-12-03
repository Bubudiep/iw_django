# Generated by Django 5.1.3 on 2024-12-03 10:27

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quan_ly_nhan_luc", "0005_company_staff_socket_id"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="company_type",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="file_safe",
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
                ("name", models.CharField(blank=True, max_length=200, null=True)),
                ("data", models.FileField(blank=True, null=True, upload_to="")),
                ("size", models.TextField(blank=True, null=True)),
                ("fileType", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="company_staff_profile",
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
                ("last_name", models.CharField(blank=True, max_length=200, null=True)),
                ("first_name", models.CharField(blank=True, max_length=200, null=True)),
                ("full_name", models.CharField(blank=True, max_length=200, null=True)),
                ("nick_name", models.CharField(blank=True, max_length=200, null=True)),
                ("isOnline", models.BooleanField(blank=True, default=False, null=True)),
                (
                    "isValidate",
                    models.BooleanField(blank=True, default=False, null=True),
                ),
                ("socket_id", models.CharField(blank=True, max_length=200, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "avatar",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="avatar_img",
                        to="quan_ly_nhan_luc.image_safe",
                    ),
                ),
                (
                    "background",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="background_img",
                        to="quan_ly_nhan_luc.image_safe",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="quan_ly_nhan_luc.company_staff",
                    ),
                ),
                (
                    "cv_file",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="quan_ly_nhan_luc.file_safe",
                    ),
                ),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
    ]