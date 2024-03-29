# Generated by Django 4.1.2 on 2023-02-02 17:04

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oceandbs', '0020_alter_acceptedtoken_paymentmethod_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='storage',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='oceandbs.storage'),
        ),
        migrations.AlterField(
            model_name='quote',
            name='expiration',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 2, 17, 34, 7, 719831, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='quote',
            name='nonce',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 26, 17, 4, 7, 719811, tzinfo=datetime.timezone.utc)),
        ),
    ]
