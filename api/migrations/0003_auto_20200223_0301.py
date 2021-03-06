# Generated by Django 3.0.3 on 2020-02-23 03:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_order_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Customer'),
        ),
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.Product'),
        ),
    ]
