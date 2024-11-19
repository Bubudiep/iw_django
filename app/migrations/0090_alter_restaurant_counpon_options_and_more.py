# Generated by Django 5.0.6 on 2024-11-19 00:59
import django.utils.timezone
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0089_remove_restaurant_socket_user_restaurant_socket_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='restaurant_counpon',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_counpon_history',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_layout',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_menu',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_menu_groups',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_menu_marks',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_order',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_order_items',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_space',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_space_group',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='restaurant_staff',
            options={'ordering': ['-id']},
        ),
        migrations.AddField(
            model_name='restaurant_menu',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant_menu',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='restaurant_menu_groups',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant_menu_groups',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='restaurant_menu_items',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant_menu_items',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='restaurant_menu_marks',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant_menu_marks',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='restaurant_order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant_order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='restaurant_order_items',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant_order_items',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='useractionlog',
            name='action_from',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='useractionlog',
            name='restaurant_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.restaurant'),
        ),
        migrations.AlterField(
            model_name='useractionlog',
            name='menu_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.restaurant_menu_items'),
        ),
    ]