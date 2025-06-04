from django.core.management.base import BaseCommand
from usuarios.models import Usuario
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

class Command(BaseCommand):
    help = 'Asegura que todos los usuarios con rol "administrador" tengan los permisos correctos'

    def handle(self, *args, **options):
        # Obtener todos los usuarios con rol administrador
        administradores = Usuario.objects.filter(rol='administrador')
        
        # Contador para mostrar mensaje
        actualizados = 0
        
        # Actualizar cada administrador
        for admin in administradores:
            cambios = []
            if not admin.is_superuser:
                admin.is_superuser = True
                cambios.append('is_superuser')
            if not admin.is_staff:
                admin.is_staff = True
                cambios.append('is_staff')
            if not admin.activo:
                admin.activo = True
                cambios.append('activo')
            
            if cambios:
                admin.save()
                actualizados += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Actualizado {admin.username} ({admin.first_name} {admin.last_name}): {", ".join(cambios)}'
                ))
        
        if actualizados > 0:
            self.stdout.write(self.style.SUCCESS(
                f'Se han actualizado {actualizados} administradores con permisos completos.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                'Todos los administradores ya tienen los permisos correctos.'
            )) 