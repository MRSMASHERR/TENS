# Generated by Django 5.1.7 on 2025-03-17 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0004_dispositivo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paciente',
            name='edad',
            field=models.IntegerField(editable=False),
        ),
    ]
