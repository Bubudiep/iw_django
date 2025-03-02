# Generated by Django 5.1.3 on 2025-03-02 10:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quan_ly_nhan_luc", "0044_advancereasontype_company_advancetype_company"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdvanceRequestHistory",
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
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("update", "Cập nhập"),
                            ("edit", "Chỉnh sửa"),
                            ("create", "Tạo mới"),
                            ("cancel", "Hủy bỏ"),
                            ("pending", "Chờ duyệt"),
                            ("approved", "Đã duyệt"),
                            ("rejected", "Từ chối"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("old_data", models.JSONField(blank=True, null=True)),
                ("new_data", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "request",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="quan_ly_nhan_luc.advancerequest",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="advance_history_approver",
                        to="quan_ly_nhan_luc.company_staff",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
