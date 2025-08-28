#!/usr/bin/env python
"""
Script simplificado para configurar SQLite en Render
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

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

User = get_user_model()

def setup_sqlite():
    """Configurar SQLite en Render"""
    print("🚀 Configurando SQLite en Render...")
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
            print("⚠️ IMPORTANTE: Cambia la contraseña después del primer login")
        else:
            print("✅ Ya existe un superusuario")
        
        print("\n🎉 Configuración de SQLite completada exitosamente!")
        print("🌐 Tu aplicación estará disponible en: https://tens.onrender.com")
        return True
        
    except Exception as e:
        print(f"❌ Error en la configuración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = setup_sqlite()
    sys.exit(0 if success else 1) 