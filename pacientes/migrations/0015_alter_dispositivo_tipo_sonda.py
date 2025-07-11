# Generated by Django 5.1.7 on 2025-04-14 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0014_paciente_direccion_paciente_email_paciente_genero_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispositivo',
            name='tipo_sonda',
            field=models.CharField(blank=True, choices=[('FOLEY_FR_12', 'Sonda Foley fr 12'), ('FOLEY_FR_14', 'Sonda Foley fr 14'), ('FOLEY_FR_16', 'Sonda Foley fr 16'), ('FOLEY_FR_18', 'Sonda Foley fr 18'), ('FOLEY_FR_20', 'Sonda Foley fr 20'), ('NELATON', 'Sonda Nelaton'), ('GASTROSTOMIA', 'Gastrostomía'), ('NASOGASTRICA', 'Sonda Nasogástrica')], max_length=20, null=True),
        ),
    ]
