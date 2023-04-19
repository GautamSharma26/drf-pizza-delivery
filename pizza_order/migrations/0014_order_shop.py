# Generated by Django 3.2.13 on 2022-09-01 09:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pizza_order', '0013_remove_order_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shop',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='pizza_order.shop'),
            preserve_default=False,
        ),
    ]