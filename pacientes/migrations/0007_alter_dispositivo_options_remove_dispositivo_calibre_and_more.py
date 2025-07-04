# Generated by Django 5.1.7 on 2025-03-24 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacientes', '0006_paciente_curso'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dispositivo',
            options={'ordering': ['-fecha_instalacion'], 'verbose_name': 'Dispositivo', 'verbose_name_plural': 'Dispositivos'},
        ),
        migrations.RemoveField(
            model_name='dispositivo',
            name='calibre',
        ),
        migrations.RemoveField(
            model_name='dispositivo',
            name='tipo',
        ),
        migrations.AddField(
            model_name='dispositivo',
            name='categoria',
            field=models.CharField(choices=[('SONDA', 'Sonda'), ('VIA_AEREA', 'Vía Aérea'), ('VVP', 'Vía Venosa Periférica'), ('DRENAJE', 'Drenaje')], default='VVP', max_length=20),
        ),
        migrations.AddField(
            model_name='dispositivo',
            name='tipo_drenaje',
            field=models.CharField(blank=True, choices=[('TORACICO', 'Drenaje Torácico'), ('PEN_ROSE', 'Drenaje Pen Rose'), ('JACKSON_PRATT', 'Drenaje Jackson Pratt'), ('GUANTE', 'Drenaje de Guante'), ('HEMOVAC_HEMOSUC', 'Drenaje Hemovac/Hemosuc')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='dispositivo',
            name='tipo_sonda',
            field=models.CharField(blank=True, choices=[('FOLEY', 'Sonda Foley'), ('NELATON', 'Sonda Nelaton'), ('GASTROSTOMIA', 'Gastrostomía'), ('NASOGASTRICA', 'Sonda Nasogástrica')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='dispositivo',
            name='tipo_via_aerea',
            field=models.CharField(blank=True, choices=[('CANULA_MAYO', 'Cánula Mayo'), ('TUBO_ENDOTRAQUEAL', 'Tubo endotraqueal'), ('TUBO_OROTRAQUEAL', 'Tubo orotraqueal'), ('MASCARA_LARINGEA', 'Mascara laríngea'), ('SONDA_ASPIRACION', 'Sonda de aspiración'), ('SONDA_YANCAHUER', 'Sonda Yancahuer')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='dispositivo',
            name='tipo_vvp',
            field=models.CharField(blank=True, choices=[('BRANULA_14G', 'Branula 14G (Adulto)'), ('BRANULA_16G', 'Branula 16G (Adulto)'), ('BRANULA_18G', 'Branula 18G (Adulto)'), ('BRANULA_20G', 'Branula 20G (Adulto)'), ('BRANULA_22G', 'Branula 22G (Pediátrica)'), ('BRANULA_24G', 'Branula 24G (Pediátrica)')], max_length=20, null=True),
        ),
    ]
