#!/usr/bin/env python
"""
Script para crear superusuario en Django con Firebase
Este script se puede ejecutar desde Render o localmente
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management.base import CommandError

User = get_user_model()

def create_superuser():
    """Crear superusuario usando variables de entorno"""
    
    # Obtener credenciales desde variables de entorno
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    
    if not all([username, email, password]):
        print("Error: Faltan variables de entorno requeridas:")
        print("- DJANGO_SUPERUSER_USERNAME")
        print("- DJANGO_SUPERUSER_EMAIL") 
        print("- DJANGO_SUPERUSER_PASSWORD")
        return False
    
    try:
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            print(f"El usuario '{username}' ya existe.")
            return True
        
        # Crear el superusuario
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Administrador',
            last_name='Sistema',
            rol='administrador'
        )
        
        print(f"Superusuario '{username}' creado exitosamente!")
        print(f"Email: {email}")
        print(f"Rol: {user.get_rol_display()}")
        return True
        
    except Exception as e:
        print(f"Error al crear superusuario: {e}")
        return False

if __name__ == '__main__':
    success = create_superuser()
    sys.exit(0 if success else 1) 