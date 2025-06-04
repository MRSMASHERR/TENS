from django.core.management.base import BaseCommand
from usuarios.models import Usuario
from django.utils import timezone
import pytz

class Command(BaseCommand):
    help = 'Verifica el estado de los usuarios y muestra información detallada'

    def handle(self, *args, **options):
        # Configurar zona horaria local
        tz = pytz.timezone('America/Santiago')
        
        usuarios = Usuario.objects.all().order_by('username')
        total = usuarios.count()
        activos_is_active = Usuario.objects.filter(is_active=True).count()
        activos_activo = Usuario.objects.filter(activo=True).count()
        superusuarios = Usuario.objects.filter(is_superuser=True).count()
        
        self.stdout.write(self.style.SUCCESS(f'Total de usuarios: {total}'))
        self.stdout.write(self.style.SUCCESS(f'Usuarios activos (is_active=True): {activos_is_active}'))
        self.stdout.write(self.style.SUCCESS(f'Usuarios con activo=True: {activos_activo}'))
        self.stdout.write(self.style.SUCCESS(f'Superusuarios: {superusuarios}'))
        
        # Mostrar información detallada de cada usuario
        self.stdout.write('\nInformación detallada de usuarios:')
        for i, usuario in enumerate(usuarios, 1):
            self.stdout.write('-' * 50)
            self.stdout.write(f'Usuario {i} de {total}:')
            self.stdout.write(f'Username: {usuario.username}')
            self.stdout.write(f'Nombre completo: {usuario.first_name} {usuario.last_name}')
            self.stdout.write(f'Email: {usuario.email}')
            self.stdout.write(f'Rol: {usuario.get_rol_display()}')
            self.stdout.write(f'RUT: {usuario.rut}')
            self.stdout.write(f'is_active: {usuario.is_active}')
            self.stdout.write(f'activo: {usuario.activo}')
            self.stdout.write(f'is_superuser: {usuario.is_superuser}')
            self.stdout.write(f'es_paciente: {usuario.es_paciente}')
            
            # Formatear fechas en zona horaria local
            fecha_registro = usuario.date_joined.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
            self.stdout.write(f'Fecha de registro: {fecha_registro}')
            
            if usuario.last_login:
                ultimo_login = usuario.last_login.astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
                self.stdout.write(f'Último login: {ultimo_login}')
            else:
                self.stdout.write('Último login: Nunca')
        
        # Verificar si hay inconsistencias
        self.stdout.write('-' * 50)
        self.stdout.write('\nVerificación de inconsistencias:')
        inconsistencias = 0
        for usuario in usuarios:
            if usuario.is_active != usuario.activo:
                inconsistencias += 1
                self.stdout.write(self.style.ERROR(
                    f'INCONSISTENCIA: Usuario {usuario.username} tiene is_active={usuario.is_active} y activo={usuario.activo}'
                ))
        
        if inconsistencias == 0:
            self.stdout.write(self.style.SUCCESS('No se encontraron inconsistencias entre is_active y activo'))
        else:
            self.stdout.write(self.style.ERROR(f'Se encontraron {inconsistencias} inconsistencias'))
            
        self.stdout.write('\nVerificación completada.') 