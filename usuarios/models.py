from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone

class Usuario(AbstractUser):
    ROLES = [
        ('administrador', 'Administrador'),
        ('docente', 'Docente'),
        ('estudiante', 'Estudiante'),
    ]
    
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True, default='')
    rol = models.CharField(max_length=20, choices=ROLES, default='estudiante')
    activo = models.BooleanField(default=True)
    es_paciente = models.BooleanField(default=False)
    
    # Campos adicionales para docentes
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    titulo_profesional = models.CharField(max_length=100, blank=True, null=True)
    anos_experiencia = models.IntegerField(default=0, blank=True, null=True)
    
    # Campos adicionales para estudiantes
    matricula = models.CharField(max_length=20, blank=True, null=True)
    ano_ingreso = models.IntegerField(blank=True, null=True)
    semestre_actual = models.IntegerField(blank=True, null=True)
    
    def get_initials(self):
        """Obtiene las iniciales del nombre y apellido del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.username:
            return self.username[0].upper()
        return "U"
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_perfil_info(self):
        """Retorna la información del perfil según el rol del usuario"""
        if self.rol == 'docente':
            return {
                'especialidad': self.especialidad or 'No especificada',
                'titulo': self.titulo_profesional or 'No especificado',
                'experiencia': f"{self.anos_experiencia} años",
            }
        elif self.rol == 'estudiante':
            return {
                'matricula': self.matricula or 'No especificada',
                'ano_ingreso': self.ano_ingreso or 'No especificado',
                'semestre': self.semestre_actual or 'No especificado',
            }
        return {}

    def save(self, *args, **kwargs):
        # Asegurar que is_active y activo estén sincronizados
        self.is_active = self.activo
        
        # Si el usuario es administrador, asegurar que tenga permisos completos
        if self.rol == 'administrador':
            self.is_superuser = True
            self.is_staff = True
        
        super().save(*args, **kwargs)

class Notificacion(models.Model):
    TIPO_CHOICES = (
        ('INFO', 'Información'),
        ('WARNING', 'Advertencia'),
        ('DANGER', 'Peligro'),
        ('SUCCESS', 'Éxito'),
    )
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='INFO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    url = models.CharField(max_length=200, blank=True, null=True)  # URL opcional para redirección
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"
    
    class Meta:
        ordering = ['-fecha_creacion']

class ConfiguracionUsuario(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='configuracion')
    recibir_notificaciones_email = models.BooleanField(default=True)
    tema_oscuro = models.BooleanField(default=False)
    mostrar_acciones_rapidas = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Configuración de {self.usuario.username}"

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    codigo = models.CharField(max_length=20, unique=True)
    docente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='cursos_dictados')
    estudiantes = models.ManyToManyField(Usuario, related_name='cursos_inscritos', blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.codigo}"

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-fecha_creacion']

class InvitacionCurso(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='invitaciones')
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    aceptada = models.BooleanField(default=False)
    enviada_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='invitaciones_enviadas')
    
    def __str__(self):
        return f"Invitación para {self.email} al curso {self.curso.nombre}"
        
    def save(self, *args, **kwargs):
        # Establecer fecha de expiración por defecto (7 días)
        if not self.fecha_expiracion:
            self.fecha_expiracion = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
        
    def esta_expirada(self):
        return timezone.now() > self.fecha_expiracion
        
    class Meta:
        verbose_name = "Invitación a curso"
        verbose_name_plural = "Invitaciones a cursos"
        unique_together = ('curso', 'email')  # Evitar invitaciones duplicadas
