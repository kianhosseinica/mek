# Generated by Django 5.1.6 on 2025-03-20 22:13

import store.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_auto_20250320_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariation',
            name='variation_id',
            field=models.CharField(blank=True, default=store.models.generate_variation_id, editable=False, max_length=20, unique=True),
        ),
    ]
