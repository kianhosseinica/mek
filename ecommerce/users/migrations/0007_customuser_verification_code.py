# Generated by Django 5.1.6 on 2025-04-01 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_customuser_is_pos_customuser_pos_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='verification_code',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]
