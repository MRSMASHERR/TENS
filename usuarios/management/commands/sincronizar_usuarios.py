from django.core.management.base import BaseCommand
from usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Sincroniza los campos is_active y activo de todos los usuarios de forma bidireccional'

    def add_arguments(self, parser):
        parser.add_argument(
            '--direccion',
            choices=['is_active_to_activo', 'activo_to_is_active'],
            help='Dirección de la sincronización: is_active_to_activo (por defecto) o activo_to_is_active'
        )
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Forzar la sincronización incluso si los campos ya están sincronizados'
        )

    def handle(self, *args, **options):
        usuarios = Usuario.objects.all()
        count = 0
        direccion = options.get('direccion', 'is_active_to_activo')
        forzar = options.get('forzar', False)
        
        for usuario in usuarios:
            # Determinar si necesitamos sincronizar
            necesita_sincronizacion = usuario.is_active != usuario.activo or forzar
            
            if necesita_sincronizacion:
                if direccion == 'activo_to_is_active':
                    # activo es la fuente de verdad
                    usuario.is_active = usuario.activo
                    usuario.save(update_fields=['is_active'])
                else:
                    # is_active es la fuente de verdad (comportamiento por defecto)
                    usuario.activo = usuario.is_active
                    usuario.save(update_fields=['activo'])
                
                count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Usuario {usuario.username} sincronizado (is_active={usuario.is_active}, activo={usuario.activo})'
                ))
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Todos los usuarios ya están sincronizados'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Se sincronizaron {count} usuarios')) 