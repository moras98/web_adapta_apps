# Generated by Django 4.2.1 on 2023-05-16 21:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('servicios_adapta_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='punto',
            name='nombre',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
