# Generated by Django 5.1.3 on 2025-03-02 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quan_ly_nhan_luc", "0045_advancerequesthistory"),
    ]

    operations = [
        migrations.AddField(
            model_name="advancerequesthistory",
            name="comment",
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]
