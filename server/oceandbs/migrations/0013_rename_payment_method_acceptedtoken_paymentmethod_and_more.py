# Generated by Django 4.1.2 on 2022-11-22 12:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oceandbs', '0012_rename_chain_id_paymentmethod_chainid_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='acceptedtoken',
            old_name='payment_method',
            new_name='paymentMethod',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='payment_method',
            new_name='paymentMethod',
        ),
    ]