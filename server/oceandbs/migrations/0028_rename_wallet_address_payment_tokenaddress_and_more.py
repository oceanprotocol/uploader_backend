# Generated by Django 4.1.2 on 2023-04-17 16:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oceandbs', '0027_alter_quote_expiration_alter_quote_nonce_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='wallet_address',
            new_name='tokenAddress',
        ),
        migrations.AddField(
            model_name='payment',
            name='userAddress',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='quote',
            name='expiration',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 17, 17, 26, 44, 632762, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='quote',
            name='nonce',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 10, 16, 56, 44, 632744, tzinfo=datetime.timezone.utc)),
        ),
    ]
