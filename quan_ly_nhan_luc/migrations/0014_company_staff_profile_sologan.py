# Generated by Django 5.1.3 on 2024-12-09 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "quan_ly_nhan_luc",
            "0013_rename_socket_id_company_staff_profile_birthday_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="company_staff_profile",
            name="sologan",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
