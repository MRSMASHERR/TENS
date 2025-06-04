from django.db import models
from pacientes.models import Paciente
from usuarios.models import Usuario

class Evolucion(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='evoluciones')
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    registro = models.TextField()
    indicaciones = models.TextField(blank=True, null=True)
    responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='evoluciones_registradas')
    
    def __str__(self):
        return f"{self.paciente} - {self.fecha} {self.hora}"
    
    class Meta:
        ordering = ['-fecha', '-hora']
