# Generated by Django 4.1.2 on 2023-02-13 14:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oceandbs', '0022_paymentmethod_rpcendpointurl_alter_quote_expiration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='expiration',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 13, 15, 16, 28, 315596, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='quote',
            name='nonce',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 6, 14, 46, 28, 315577, tzinfo=datetime.timezone.utc)),
        ),
    ]
