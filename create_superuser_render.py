#!/usr/bin/env python
"""
Script para crear un superusuario automáticamente en Render
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

User = get_user_model()

def create_superuser():
    """Crear un superusuario si no existe"""
    print("👤 Verificando superusuarios...")
    
    # Verificar si ya existe un superusuario
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Ya existe un superusuario")
        return
    
    # Crear superusuario con credenciales por defecto
    try:
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        email = os.environ.get('ADMIN_EMAIL', 'admin@sistema-medico.com')
        password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
        
        # Crear el superusuario
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Administrador',
            last_name='Sistema',
            rol='administrador'
        )
        
        print(f"✅ Superusuario creado exitosamente:")
        print(f"   Usuario: {username}")
        print(f"   Email: {email}")
        print(f"   Contraseña: {password}")
        print("⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        
    except Exception as e:
        print(f"❌ Error al crear superusuario: {e}")

def main():
    """Función principal"""
    print("🚀 Creando superusuario para Render...")
    create_superuser()

if __name__ == '__main__':
    main() 