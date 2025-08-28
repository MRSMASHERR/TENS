#!/usr/bin/env python
"""
Script de inicialización para Render
Ejecuta migraciones y crea superusuario automáticamente
"""

import os
import sys
import django
import subprocess

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
django.setup()

def run_command(command):
    """Ejecutar un comando de Django"""
    try:
        result = subprocess.run(
            ['python', 'manage.py'] + command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {command}: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {command}: {e.stderr}")
        # Si es un error de migración, intentar con --run-syncdb
        if 'migrate' in command and 'database' in e.stderr.lower():
            print("🔄 Intentando con --run-syncdb...")
            try:
                result = subprocess.run(
                    ['python', 'manage.py', 'migrate', '--run-syncdb'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"✅ migrate --run-syncdb: {result.stdout}")
                return True
            except subprocess.CalledProcessError as e2:
                print(f"❌ Error con --run-syncdb: {e2.stderr}")
        return False

def main():
    print("🚀 Iniciando configuración de Render...")
    
    # 1. Ejecutar migraciones
    print("\n📦 Ejecutando migraciones...")
    if not run_command("migrate"):
        print("⚠️ Migración falló, intentando configuración alternativa...")
        # Intentar con el script de configuración robusta
        try:
            import setup_database
            if setup_database.main():
                print("✅ Configuración alternativa exitosa")
            else:
                print("❌ Falló la configuración alternativa")
                return False
        except Exception as e:
            print(f"❌ Error en configuración alternativa: {e}")
            return False
    
    # 2. Recolectar archivos estáticos
    print("\n📁 Recolectando archivos estáticos...")
    if not run_command("collectstatic --noinput"):
        print("❌ Falló la recolección de estáticos")
        return False
    
    # 3. Crear superusuario automáticamente
    print("\n👤 Creando superusuario...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Verificar si ya existe un superusuario
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
    except Exception as e:
        print(f"⚠️ Error al crear superusuario: {e}")
    
    print("\n🎉 Configuración completada!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 