# Generated by Django 5.0.2 on 2024-10-15 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_alter_album_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='level',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
