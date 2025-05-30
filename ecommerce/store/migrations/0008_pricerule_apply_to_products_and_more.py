# Generated by Django 5.1.6 on 2025-03-20 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_productvariation_custom_sku_productvariation_ean_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricerule',
            name='apply_to_products',
            field=models.ManyToManyField(blank=True, help_text='Apply to these products', related_name='applied_price_rules', to='store.product'),
        ),
        migrations.AlterField(
            model_name='pricerule',
            name='apply_to_variations',
            field=models.ManyToManyField(blank=True, help_text='Apply to specific product variations', related_name='applied_price_rules', to='store.productvariation'),
        ),
    ]
