# Generated by Django 5.1.7 on 2025-03-24 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0007_alter_dispositivo_options_remove_dispositivo_calibre_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paciente',
            name='cateter_urinario',
        ),
        migrations.RemoveField(
            model_name='paciente',
            name='vias_venosas',
        ),
    ]
