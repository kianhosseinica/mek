# Generated by Django 5.1.6 on 2025-02-27 22:34

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_refundrequest_refundmedia'),
    ]

    operations = [
        migrations.AddField(
            model_name='refundmedia',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='refundrequest',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refund_requests', to='orders.order'),
        ),
        migrations.AlterField(
            model_name='refundrequest',
            name='order_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to='orders.orderitem'),
        ),
        migrations.AlterField(
            model_name='refundrequest',
            name='restocking_fee_percentage',
            field=models.DecimalField(decimal_places=2, default=10, help_text='Restocking fee percentage applied to the refund.', max_digits=5),
        ),
    ]
