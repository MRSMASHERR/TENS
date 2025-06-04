from django.db import models
from usuarios.models import Usuario
from django.contrib.auth import get_user_model
from datetime import date

Usuario = get_user_model()

class Paciente(models.Model):
    # Opciones para campos de selección
    OPCIONES_BRAZALETE = (
        ('SI', 'Si'),
        ('NO', 'No'),
    )
    
    OPCIONES_PREVISION = (
        ('FONASA', 'Fonasa'),
        ('ISAPRE', 'Isapre'),
        ('PRAIS', 'Prais'),
        ('OTRAS', 'Otras'),
    )
    
    OPCIONES_GENERO = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )
    
    # Campos básicos
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12)  # Eliminado unique=True para permitir el mismo RUT en diferentes cursos
    fecha_nacimiento = models.DateField()
    edad = models.IntegerField(editable=False)  # Ahora será calculado automáticamente
    sala_cama = models.CharField(max_length=20)
    dias_hospitalizacion = models.IntegerField(default=0)
    fecha_ingreso = models.DateField(auto_now_add=True)
    fecha_alta = models.DateField(null=True, blank=True)
    motivo_alta = models.CharField(max_length=100, blank=True, null=True)
    alergias = models.TextField(blank=True, null=True, help_text="Indica las alergias del paciente, separadas por comas")
    
    # Campos de contacto
    genero = models.CharField(max_length=1, choices=OPCIONES_GENERO, default='O')
    genero_otro = models.CharField(max_length=50, blank=True, null=True, help_text="Especifique otro género")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    
    # Nuevos campos
    antecedentes_morbidos = models.TextField(blank=True, null=True, help_text="Antecedentes mórbidos del paciente")
    tabaquismo = models.BooleanField(default=False)
    alcoholismo = models.BooleanField(default=False)
    drogas = models.CharField(max_length=100, blank=True, null=True, help_text="Especifique las drogas")
    brazalete = models.CharField(max_length=2, choices=OPCIONES_BRAZALETE, default='NO')
    prevision = models.CharField(max_length=20, choices=OPCIONES_PREVISION, default='FONASA')
    prevision_otra = models.CharField(max_length=50, blank=True, null=True, help_text="Especifique otra previsión")
    
    # Campos adicionales
    motivo_consulta = models.TextField(blank=True, null=True, help_text="Motivo de consulta del paciente")
    diagnostico = models.TextField(blank=True, null=True, help_text="Diagnóstico del paciente")
    
    # Relaciones
    registrado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pacientes_registrados')
    usuario_asociado = models.OneToOneField(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='paciente_perfil')
    activo = models.BooleanField(default=True)
    curso = models.ForeignKey('usuarios.Curso', on_delete=models.CASCADE, related_name='pacientes', null=True, blank=True)
    
    def __str__(self):
        nombre_mostrar = self.nombre
        if self.genero == 'O' and self.genero_otro:
            nombre_mostrar = f"{self.nombre} ({self.genero_otro})"
        return f"{nombre_mostrar} - {self.rut}"
    
    @property
    def nombre_completo(self):
        return self.nombre
    
    @property
    def habitacion(self):
        return self.sala_cama
    
    @property
    def esta_dado_de_alta(self):
        return bool(self.fecha_alta)
    
    def se_pueden_registrar_datos(self):
        """Verifica si se pueden registrar datos en el paciente"""
        return not self.esta_dado_de_alta
    
    def calcular_edad(self):
        """Calcula la edad en años a partir de la fecha de nacimiento"""
        hoy = date.today()
        # Restamos un año si todavía no ha llegado el cumpleaños de este año
        return hoy.year - self.fecha_nacimiento.year - ((hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    
    def dar_de_alta(self, motivo=None):
        """Da de alta al paciente con la fecha actual"""
        self.fecha_alta = date.today()
        self.activo = False
        if motivo:
            self.motivo_alta = motivo
        self.save()
    
    def readmitir(self):
        """Readmite al paciente, limpiando la fecha de alta"""
        self.fecha_alta = None
        self.motivo_alta = None
        self.activo = True
        self.save()
    
    def save(self, *args, **kwargs):
        # Actualizar la edad automáticamente antes de guardar
        if self.fecha_nacimiento:
            self.edad = self.calcular_edad()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['nombre']
        unique_together = ['rut', 'curso']  # Restricción: un RUT solo puede aparecer una vez en cada curso

class Dispositivo(models.Model):
    # Categorías principales de dispositivos
    CATEGORIA_CHOICES = (
        ('SONDA', 'Sonda'),
        ('VIA_AEREA', 'Vía Aérea'),
        ('VVP', 'Vía Venosa Periférica'),
        ('DRENAJE', 'Drenaje'),
    )
    
    # Tipos específicos de dispositivos por categoría
    TIPO_SONDA_CHOICES = (
        ('FOLEY_FR_12', 'Sonda Foley fr 12'),
        ('FOLEY_FR_14', 'Sonda Foley fr 14'),
        ('FOLEY_FR_16', 'Sonda Foley fr 16'),
        ('FOLEY_FR_18', 'Sonda Foley fr 18'),
        ('FOLEY_FR_20', 'Sonda Foley fr 20'),
        ('NELATON', 'Sonda Nelaton'),
        ('GASTROSTOMIA', 'Gastrostomía'),
        ('NASOGASTRICA', 'Sonda Nasogástrica'),
    )
    
    TIPO_VIA_AEREA_CHOICES = (
        ('CANULA_MAYO', 'Cánula Mayo'),
        ('TUBO_ENDOTRAQUEAL', 'Tubo endotraqueal'),
        ('TUBO_OROTRAQUEAL', 'Tubo orotraqueal'),
        ('MASCARA_LARINGEA', 'Mascara laríngea'),
        ('SONDA_ASPIRACION', 'Sonda de aspiración'),
        ('SONDA_YANCAHUER', 'Sonda Yancahuer'),
    )
    
    TIPO_VVP_CHOICES = (
        ('BRANULA_14G', 'Branula 14G (Adulto)'),
        ('BRANULA_16G', 'Branula 16G (Adulto)'),
        ('BRANULA_18G', 'Branula 18G (Adulto)'),
        ('BRANULA_20G', 'Branula 20G (Adulto)'),
        ('BRANULA_22G', 'Branula 22G (Pediátrica)'),
        ('BRANULA_24G', 'Branula 24G (Pediátrica)'),
    )
    
    TIPO_DRENAJE_CHOICES = (
        ('TORACICO', 'Drenaje Torácico'),
        ('PEN_ROSE', 'Drenaje Pen Rose'),
        ('JACKSON_PRATT', 'Drenaje Jackson Pratt'),
        ('GUANTE', 'Drenaje de Guante'),
        ('HEMOVAC_HEMOSUC', 'Drenaje Hemovac/Hemosuc'),
    )
    
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='dispositivos')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='VVP')
    tipo_sonda = models.CharField(max_length=20, choices=TIPO_SONDA_CHOICES, blank=True, null=True)
    tipo_via_aerea = models.CharField(max_length=20, choices=TIPO_VIA_AEREA_CHOICES, blank=True, null=True)
    tipo_vvp = models.CharField(max_length=20, choices=TIPO_VVP_CHOICES, blank=True, null=True)
    tipo_drenaje = models.CharField(max_length=20, choices=TIPO_DRENAJE_CHOICES, blank=True, null=True)
    fecha_instalacion = models.DateField()
    dias_instalacion = models.IntegerField(default=1)
    fecha_retiro = models.DateField(null=True, blank=True)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    def get_tipo_display_completo(self):
        """Retorna el nombre completo del tipo de dispositivo según su categoría"""
        if self.categoria == 'SONDA' and self.tipo_sonda:
            return dict(self.TIPO_SONDA_CHOICES).get(self.tipo_sonda)
        elif self.categoria == 'VIA_AEREA' and self.tipo_via_aerea:
            return dict(self.TIPO_VIA_AEREA_CHOICES).get(self.tipo_via_aerea)
        elif self.categoria == 'VVP' and self.tipo_vvp:
            return dict(self.TIPO_VVP_CHOICES).get(self.tipo_vvp)
        elif self.categoria == 'DRENAJE' and self.tipo_drenaje:
            return dict(self.TIPO_DRENAJE_CHOICES).get(self.tipo_drenaje)
        return "No especificado"
    
    def debe_retirarse(self):
        """Verifica si el dispositivo debe retirarse basado en los días de instalación"""
        if self.fecha_retiro:
            return True
        
        from datetime import date, timedelta
        fecha_fin = self.fecha_instalacion + timedelta(days=self.dias_instalacion)
        return date.today() >= fecha_fin
    
    def calcular_fecha_retiro(self):
        """Calcula la fecha de retiro basada en la fecha de instalación y días de instalación"""
        from datetime import timedelta
        return self.fecha_instalacion + timedelta(days=self.dias_instalacion)
    
    def marcar_como_retirado(self):
        """Marca el dispositivo como retirado estableciendo la fecha de retiro"""
        from datetime import date
        if not self.fecha_retiro:
            self.fecha_retiro = date.today()
            self.save()
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para calcular la fecha de retiro si no está definida"""
        # Si se está guardando por primera vez y no tiene fecha de retiro
        # asignar automáticamente la fecha basada en la instalación y días
        if not self.fecha_retiro and self.dias_instalacion > 0:
            self.fecha_retiro = self.calcular_fecha_retiro()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_tipo_display_completo()} - {self.paciente.nombre}"
    
    class Meta:
        ordering = ['-fecha_instalacion']
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
