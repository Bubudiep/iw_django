# Generated by Django 5.0.2 on 2024-10-20 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0048_rename_sodientieuthu_lichsutieuthu_sodienbatdau_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='phong',
            name='sodienbandau',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='phong',
            name='sonuocbandau',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]