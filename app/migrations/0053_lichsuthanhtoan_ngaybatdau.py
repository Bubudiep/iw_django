# Generated by Django 5.0.2 on 2024-10-20 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0052_remove_lichsutieuthu_nguoitro_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lichsuthanhtoan',
            name='ngayBatdau',
            field=models.DateField(blank=True, null=True),
        ),
    ]