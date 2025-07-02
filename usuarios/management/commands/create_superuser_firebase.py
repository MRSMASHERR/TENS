from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Crear superusuario para Firebase usando variables de entorno'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario del superusuario',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email del superusuario',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Contraseña del superusuario',
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Administrador',
            help='Nombre del superusuario',
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='Sistema',
            help='Apellido del superusuario',
        )

    def handle(self, *args, **options):
        # Obtener credenciales desde argumentos o variables de entorno
        username = options['username'] or os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = options['email'] or os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = options['password'] or os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        first_name = options['first_name']
        last_name = options['last_name']

        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR(
                    'Error: Debes proporcionar username, email y password '
                    'como argumentos o variables de entorno:\n'
                    '- DJANGO_SUPERUSER_USERNAME\n'
                    '- DJANGO_SUPERUSER_EMAIL\n'
                    '- DJANGO_SUPERUSER_PASSWORD'
                )
            )
            return

        try:
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'El usuario "{username}" ya existe.')
                )
                return

            # Crear el superusuario
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                rol='administrador'
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Superusuario "{username}" creado exitosamente!\n'
                    f'Email: {email}\n'
                    f'Rol: {user.get_rol_display()}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear superusuario: {e}')
            ) 