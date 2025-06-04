from django.core.management.base import BaseCommand
from usuarios.models import Usuario
from pacientes.models import Paciente
from django.urls import get_resolver
from django.db import connection

class Command(BaseCommand):
    help = 'Verifica el estado del sistema y la configuración'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("---- VERIFICACIÓN DEL SISTEMA ----"))

        # Verificar usuarios y roles
        total_usuarios = Usuario.objects.count()
        admins = Usuario.objects.filter(rol='administrador').count()
        docentes = Usuario.objects.filter(rol='docente').count()
        estudiantes = Usuario.objects.filter(rol='estudiante').count()
        
        self.stdout.write(f"Total de usuarios: {total_usuarios}")
        self.stdout.write(f"Administradores: {admins}")
        self.stdout.write(f"Docentes: {docentes}")
        self.stdout.write(f"Estudiantes: {estudiantes}")

        # Verificar permisos de administrador
        admins_list = Usuario.objects.filter(rol='administrador')
        for admin in admins_list:
            self.stdout.write(f"Admin: {admin.username} | is_superuser: {admin.is_superuser} | is_staff: {admin.is_staff} | activo: {admin.activo}")

        # Verificar rutas
        self.stdout.write("\n---- RUTAS DISPONIBLES ----")
        all_urls = self._get_all_urls()
        admin_urls = [url for url in all_urls if 'admin' in url]
        for url in admin_urls:
            self.stdout.write(f"URL admin: {url}")

        # Verificar pacientes
        self.stdout.write("\n---- PACIENTES ----")
        total_pacientes = Paciente.objects.count()
        activos = Paciente.objects.filter(fecha_alta__isnull=True).count()
        dados_alta = Paciente.objects.filter(fecha_alta__isnull=False).count()
        
        self.stdout.write(f"Total pacientes: {total_pacientes}")
        self.stdout.write(f"Pacientes activos: {activos}")
        self.stdout.write(f"Pacientes dados de alta: {dados_alta}")

        # Verificar base de datos
        self.stdout.write("\n---- BASE DE DATOS ----")
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM usuarios_usuario WHERE rol='administrador'")
            db_admins = cursor.fetchone()[0]
            
            cursor.execute("SELECT count(*) FROM usuarios_usuario WHERE rol='docente'")
            db_docentes = cursor.fetchone()[0]
            
            cursor.execute("SELECT count(*) FROM usuarios_usuario WHERE rol='estudiante'")
            db_estudiantes = cursor.fetchone()[0]
        
        self.stdout.write(f"Administradores en DB: {db_admins}")
        self.stdout.write(f"Docentes en DB: {db_docentes}")
        self.stdout.write(f"Estudiantes en DB: {db_estudiantes}")

    def _get_all_urls(self):
        """Returns all URLs defined in urls.py"""
        urls = []
        resolver = get_resolver()
        for url_pattern in resolver.url_patterns:
            if hasattr(url_pattern, 'pattern'):
                urls.append(str(url_pattern.pattern))
            else:
                urls.append(str(url_pattern))
        return urls 