# Generated by Django 5.1.3 on 2024-12-22 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0115_nhanviensorting"),
    ]

    operations = [
        migrations.AddField(
            model_name="danhsachnhanvien_record",
            name="isDilam",
            field=models.BooleanField(default=True),
        ),
    ]
