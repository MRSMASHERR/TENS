# Generated by Django 5.1.7 on 2025-03-13 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paciente',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]
