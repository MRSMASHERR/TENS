# Generated by Django 5.1.7 on 2025-03-18 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_curso_invitacioncurso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='anos_experiencia',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
