# Generated by Django 5.1.3 on 2024-11-09 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0073_restaurant_layout_avatar"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="restaurant_layout",
            name="avatar",
        ),
        migrations.AddField(
            model_name="restaurant",
            name="avatar",
            field=models.TextField(blank=True, null=True),
        ),
    ]
