# Generated by Django 4.1.2 on 2022-11-21 14:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('oceandbs', '0007_storage_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quote',
            options={'ordering': ['created']},
        ),
        migrations.AlterModelOptions(
            name='storage',
            options={'ordering': ['created']},
        ),
        migrations.AddField(
            model_name='quote',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='storage',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
