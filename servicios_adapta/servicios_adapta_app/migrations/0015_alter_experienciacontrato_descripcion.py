# Generated by Django 4.2.2 on 2023-08-04 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicios_adapta_app', '0014_experienciacontrato_descripcion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experienciacontrato',
            name='descripcion',
            field=models.TextField(blank=True, default='exit'),
            preserve_default=False,
        ),
    ]
