# Generated by Django 5.1.3 on 2024-11-10 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0077_restaurant_socket"),
    ]

    operations = [
        migrations.AddField(
            model_name="restaurant",
            name="mohinh",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
