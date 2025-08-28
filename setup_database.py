#!/usr/bin/env python
"""
Script para configurar la base de datos de manera robusta
"""
import os
import sys
import django
import subprocess
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print("🔍 Verificando conexión a la base de datos...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexión a la base de datos exitosa")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def setup_database():
    """Configurar la base de datos"""
    print("🗄️ Configurando base de datos...")
    
    # Verificar si la base de datos está configurada
    if not check_database_connection():
        print("⚠️ No se puede conectar a la base de datos")
        return False
    
    # Intentar migraciones
    try:
        print("🔄 Ejecutando migraciones...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=0'])
        print("✅ Migraciones completadas")
        return True
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        
        # Intentar con --run-syncdb
        try:
            print("🔄 Intentando con --run-syncdb...")
            execute_from_command_line(['manage.py', 'migrate', '--run-syncdb', '--verbosity=0'])
            print("✅ Migraciones con --run-syncdb completadas")
            return True
        except Exception as e2:
            print(f"❌ Error con --run-syncdb: {e2}")
            return False

def create_superuser():
    """Crear superusuario si no existe"""
    print("👤 Verificando superusuario...")
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            username = os.environ.get('ADMIN_USERNAME', 'admin')
            email = os.environ.get('ADMIN_EMAIL', 'admin@sistema-medico.com')
            password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
            
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='Sistema',
                rol='administrador'
            )
            print(f"✅ Superusuario creado: {username}")
            print(f"   Email: {email}")
            print(f"   Contraseña: {password}")
        else:
            print("✅ Ya existe un superusuario")
        return True
    except Exception as e:
        print(f"❌ Error al crear superusuario: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Configurando base de datos...")
    print("=" * 50)
    
    # Configurar base de datos
    if setup_database():
        # Crear superusuario
        create_superuser()
        print("\n🎉 Configuración completada exitosamente!")
        return True
    else:
        print("\n❌ Error en la configuración de la base de datos")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 