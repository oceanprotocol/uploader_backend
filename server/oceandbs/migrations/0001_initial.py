# Generated by Django 4.1.2 on 2022-10-25 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[['waiting', 'Waiting for transaction'], ['done', 'Payment done'], ['refunded', 'Payment refunded']], max_length=256, null=True)),
                ('wallet_address', models.CharField(max_length=256, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chainId', models.CharField(max_length=256)),
                ('title', models.CharField(max_length=256)),
                ('wallet_address', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=256, verbose_name='Storage type')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Storage description')),
                ('paymentMethods', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_methods', to='oceandbs.paymentmethod')),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField()),
                ('wallet_address', models.CharField(max_length=256, null=True)),
                ('upload_status', models.CharField(choices=[('200', 'Quote exists'), ('201', 'Quote created')], max_length=256, null=True)),
                ('payment', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quote', to='oceandbs.payment')),
                ('storage', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quotes', to='oceandbs.storage')),
            ],
        ),
        migrations.AddField(
            model_name='payment',
            name='paymentMethod',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='oceandbs.paymentmethod'),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_url', models.CharField(max_length=255)),
                ('content_type', models.CharField(default='None', max_length=255)),
                ('stored_url', models.CharField(blank=True, max_length=255)),
                ('object_content', models.BinaryField(blank=True)),
                ('is_bytes', models.BooleanField(default=False)),
                ('quote', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='oceandbs.quote')),
            ],
        ),
    ]
