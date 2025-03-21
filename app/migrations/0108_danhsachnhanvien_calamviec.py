# Generated by Django 5.1.3 on 2024-11-25 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0107_restaurant_bankname"),
    ]

    operations = [
        migrations.AddField(
            model_name="danhsachnhanvien",
            name="calamviec",
            field=models.CharField(
                choices=[
                    ("cangay", "cangay"),
                    ("cadem", "cadem"),
                    ("ca1", "ca1"),
                    ("ca2", "ca2"),
                    ("ca3", "ca3"),
                    ("hanhchinh", "hanhchinh"),
                    ("khac", "khac"),
                ],
                default="cangay",
                max_length=50,
            ),
        ),
    ]
