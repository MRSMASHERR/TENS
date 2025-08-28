#!/usr/bin/env python
"""
Script específico para configurar Render con SQLite
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')

# Forzar SQLite antes de configurar Django
os.environ['FORCE_SQLITE'] = 'True'

django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

User = get_user_model()

def setup_render():
    """Configurar Render con SQLite"""
    print("🚀 Configurando Render con SQLite...")
    print("=" * 50)
    
    try:
        # 1. Recolectar archivos estáticos
        print("📦 Recolectando archivos estáticos...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--verbosity=0'])
        print("✅ Archivos estáticos recolectados")
        
        # 2. Ejecutar migraciones
        print("🔄 Ejecutando migraciones...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=0'])
        print("✅ Migraciones completadas")
        
        # 3. Crear superusuario
        print("👤 Verificando superusuario...")
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
        
        print("\n🎉 Configuración de Render completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en la configuración: {e}")
        return False

if __name__ == '__main__':
    success = setup_render()
    sys.exit(0 if success else 1) 