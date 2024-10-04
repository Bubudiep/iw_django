# Generated by Django 5.0.2 on 2024-10-02 16:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_alter_bangluongtheochucvu_mucluong_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tuchamcongtay',
            name='ca',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.kieuca'),
        ),
        migrations.AddField(
            model_name='tuchamcongtay',
            name='kieungay',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.kieungay'),
        ),
    ]