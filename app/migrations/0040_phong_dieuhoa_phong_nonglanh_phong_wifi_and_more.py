# Generated by Django 5.0.6 on 2024-10-17 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_alter_nguoitro_tamtru'),
    ]

    operations = [
        migrations.AddField(
            model_name='phong',
            name='dieuhoa',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='phong',
            name='nonglanh',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='phong',
            name='wifi',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='phong',
            name='giaPhong',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]