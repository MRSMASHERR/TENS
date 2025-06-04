from django.db import models
from pacientes.models import Paciente
from usuarios.models import Usuario

class BalanceHidrico(models.Model):
    HORARIOS = (
        ('09:00', '09:00'),
        ('13:00', '13:00'),
        ('17:00', '17:00'),
        ('21:00', '21:00'),
        ('01:00', '01:00'),
        ('06:00', '06:00'),
    )
    
    PRESENCIA_CHOICES = (
        ('+', 'Presente'),
        ('-', 'Ausente'),
    )
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='balances_hidricos')
    fecha = models.DateField(auto_now_add=True)
    hora = models.CharField(max_length=5, choices=HORARIOS)
    
    # Ingresos (ml)
    agua = models.IntegerField(default=0, verbose_name='Agua')
    soluciones = models.IntegerField(default=0, verbose_name='Soluciones')
    alimentos = models.IntegerField(default=0, verbose_name='Alimentos')
    medicamentos_sueros = models.IntegerField(default=0, verbose_name='Medicamentos/Sueros')
    
    # Egresos
    orina = models.IntegerField(default=0, verbose_name='Orina')
    deposiciones = models.CharField(max_length=1, choices=PRESENCIA_CHOICES, default='-', verbose_name='Deposiciones')
    vomito = models.CharField(max_length=1, choices=PRESENCIA_CHOICES, default='-', verbose_name='Vómito')
    hemoderivado = models.IntegerField(default=0, verbose_name='Hemoderivado')
    drenaje = models.IntegerField(default=0, verbose_name='Drenaje')
    
    observaciones = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    @property
    def total_ingresos(self):
        return self.agua + self.soluciones + self.alimentos + self.medicamentos_sueros
    
    @property
    def total_egresos(self):
        # Contamos todos los egresos medibles en ml
        return self.orina + self.hemoderivado + self.drenaje
    
    @property
    def balance_total(self):
        return self.total_ingresos - self.total_egresos
    
    def __str__(self):
        return f"{self.paciente} - {self.fecha} {self.hora}"
    
    class Meta:
        unique_together = ('paciente', 'fecha', 'hora')
        ordering = ['-fecha', 'hora']
