# Generated by Django 4.2.2 on 2023-07-27 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicios_adapta_app', '0012_alter_experienciacontrato_fechafin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experienciacontrato',
            name='fechaFin',
            field=models.DateField(blank=True, null=True),
        ),
    ]