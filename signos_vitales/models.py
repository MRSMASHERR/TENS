from django.db import models
from pacientes.models import Paciente
from usuarios.models import Usuario

class SignosVitales(models.Model):
    HORARIOS = (
        ('09:00', '09:00'),
        ('13:00', '13:00'),
        ('17:00', '17:00'),
        ('21:00', '21:00'),
        ('01:00', '01:00'),
        ('07:00', '07:00'),
    )
    
    ESTADO_HGT_CHOICES = (
        ('ayuno', 'En ayunas'),
        ('postprandial', 'Post prandial'),
        ('', 'No especificado'),
    )
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='signos_vitales')
    fecha = models.DateField(auto_now_add=True)
    hora = models.CharField(max_length=5, choices=HORARIOS)
    presion_arterial = models.CharField(max_length=10)  # Formato: 120/80
    frecuencia_cardiaca = models.IntegerField()
    saturacion = models.IntegerField()
    fio2 = models.IntegerField(null=True, blank=True)
    frecuencia_respiratoria = models.IntegerField()
    temperatura = models.DecimalField(max_digits=4, decimal_places=1)
    hgt = models.IntegerField(null=True, blank=True)  # Hemoglucotest
    estado_hgt = models.CharField(max_length=15, choices=ESTADO_HGT_CHOICES, blank=True, default='')
    eva = models.IntegerField(null=True, blank=True)  # Escala Visual Analógica (dolor)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.paciente} - {self.fecha} {self.hora}"
    
    class Meta:
        unique_together = ('paciente', 'fecha', 'hora')
        ordering = ['-fecha', 'hora']
