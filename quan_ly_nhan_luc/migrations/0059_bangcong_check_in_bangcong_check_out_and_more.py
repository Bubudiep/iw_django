# Generated by Django 5.1.3 on 2025-03-24 15:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quan_ly_nhan_luc", "0058_ngaycong_bangcong_yeucausuabangcong"),
    ]

    operations = [
        migrations.AddField(
            model_name="bangcong",
            name="check_in",
            field=models.TimeField(blank=True, null=True, verbose_name="Giờ vào"),
        ),
        migrations.AddField(
            model_name="bangcong",
            name="check_out",
            field=models.TimeField(blank=True, null=True, verbose_name="Giờ ra"),
        ),
        migrations.AddField(
            model_name="bangcong",
            name="overtime_hours",
            field=models.FloatField(default=0.0, verbose_name="Giờ tăng ca"),
        ),
        migrations.AddField(
            model_name="bangcong",
            name="salary_coefficient",
            field=models.FloatField(default=1.0, verbose_name="Hệ số lương"),
        ),
        migrations.AddField(
            model_name="bangcong",
            name="total_work_hours",
            field=models.FloatField(default=0.0, verbose_name="Số giờ làm việc"),
        ),
        migrations.CreateModel(
            name="BangCongHistory",
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
                    "old_check_in",
                    models.TimeField(blank=True, null=True, verbose_name="Giờ vào cũ"),
                ),
                (
                    "old_check_out",
                    models.TimeField(blank=True, null=True, verbose_name="Giờ ra cũ"),
                ),
                (
                    "old_overtime_hours",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Giờ tăng ca cũ"
                    ),
                ),
                (
                    "old_total_work_hours",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Số giờ làm việc cũ"
                    ),
                ),
                (
                    "old_salary_coefficient",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Hệ số lương cũ"
                    ),
                ),
                (
                    "new_check_in",
                    models.TimeField(blank=True, null=True, verbose_name="Giờ vào mới"),
                ),
                (
                    "new_check_out",
                    models.TimeField(blank=True, null=True, verbose_name="Giờ ra mới"),
                ),
                (
                    "new_overtime_hours",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Giờ tăng ca mới"
                    ),
                ),
                (
                    "new_total_work_hours",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Số giờ làm việc mới"
                    ),
                ),
                (
                    "new_salary_coefficient",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Hệ số lương mới"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "bangcong",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="quan_ly_nhan_luc.bangcong",
                    ),
                ),
                (
                    "yeucau",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="quan_ly_nhan_luc.yeucausuabangcong",
                        verbose_name="Yêu cầu sửa",
                    ),
                ),
            ],
        ),
    ]
