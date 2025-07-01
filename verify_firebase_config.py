#!/usr/bin/env python
"""
Script para verificar la configuración de Firebase
"""
import os
import sys
import django
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_environment_variables():
    """Verificar variables de entorno de Firebase"""
    print("Verificando variables de entorno...")
    print("-" * 30)
    
    required_vars = [
        'FIREBASE_API_KEY',
        'FIREBASE_AUTH_DOMAIN',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET',
        'FIREBASE_MESSAGING_SENDER_ID',
        'FIREBASE_APP_ID',
        'FIREBASE_DATABASE_URL',
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var}: {value[:20]}..." if len(value) > 20 else f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: No configurada")
            missing_vars.append(var)
    
    # Verificar archivo de clave de servicio
    service_account_key = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')
    if service_account_key and os.path.exists(service_account_key):
        print(f"✓ FIREBASE_SERVICE_ACCOUNT_KEY: {service_account_key}")
    else:
        print("✗ FIREBASE_SERVICE_ACCOUNT_KEY: Archivo no encontrado")
        missing_vars.append('FIREBASE_SERVICE_ACCOUNT_KEY')
    
    return len(missing_vars) == 0

def check_python_packages():
    """Verificar paquetes de Python necesarios"""
    print("\nVerificando paquetes de Python...")
    print("-" * 30)
    
    required_packages = [
        'firebase_admin',
        'pyrebase',
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}: No instalado")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def test_firebase_connection():
    """Probar conexión con Firebase"""
    print("\nProbando conexión con Firebase...")
    print("-" * 30)
    
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
        django.setup()
        
        # Importar módulos de Firebase
        from sistema_medico.firebase_config import initialize_firebase, get_database_client
        
        # Inicializar Firebase
        app = initialize_firebase()
        print("✓ Firebase inicializado correctamente")
        
        # Probar conexión a Realtime Database
        db = get_database_client()
        print("✓ Conexión a Realtime Database establecida")
        
        # Probar operación simple
        test_ref = db.child('test_connection').child('test')
        test_ref.set({'timestamp': 'test'})
        test_ref.delete()
        print("✓ Operación de escritura/lectura exitosa")
        
        return True
        
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        return False

def check_django_configuration():
    """Verificar configuración de Django"""
    print("\nVerificando configuración de Django...")
    print("-" * 30)
    
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_medico.settings')
        django.setup()
        
        from django.conf import settings
        
        # Verificar configuración de Firebase
        if hasattr(settings, 'FIREBASE_CONFIG'):
            print("✓ Configuración de Firebase en settings.py")
        else:
            print("✗ Configuración de Firebase no encontrada en settings.py")
            return False
        
        # Verificar variable USE_FIREBASE
        if hasattr(settings, 'USE_FIREBASE'):
            print(f"✓ USE_FIREBASE: {settings.USE_FIREBASE}")
        else:
            print("✗ USE_FIREBASE no configurada")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error en configuración de Django: {e}")
        return False

def main():
    """Función principal"""
    print("Verificación de configuración de Firebase")
    print("=" * 50)
    
    # Verificar variables de entorno
    env_ok = check_environment_variables()
    
    # Verificar paquetes de Python
    packages_ok = check_python_packages()
    
    # Verificar configuración de Django
    django_ok = check_django_configuration()
    
    # Probar conexión con Firebase
    connection_ok = False
    if env_ok and packages_ok and django_ok:
        connection_ok = test_firebase_connection()
    
    # Resumen
    print("\n" + "=" * 50)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    print(f"Variables de entorno: {'✓' if env_ok else '✗'}")
    print(f"Paquetes de Python: {'✓' if packages_ok else '✗'}")
    print(f"Configuración Django: {'✓' if django_ok else '✗'}")
    print(f"Conexión Firebase: {'✓' if connection_ok else '✗'}")
    
    if env_ok and packages_ok and django_ok and connection_ok:
        print("\n🎉 ¡Configuración completa! Firebase está listo para usar.")
        print("\nPróximos pasos:")
        print("1. Ejecuta el script de migración: python migrate_to_firebase.py")
        print("2. Cambia USE_FIREBASE=True en tu archivo .env")
        print("3. Reinicia tu aplicación Django")
    else:
        print("\n⚠️  Hay problemas en la configuración. Revisa los errores arriba.")
        
        if not env_ok:
            print("\nPara configurar variables de entorno:")
            print("1. Copia firebase_env_example.txt a .env")
            print("2. Edita .env con tus credenciales de Firebase")
        
        if not packages_ok:
            print("\nPara instalar paquetes faltantes:")
            print("python install_firebase_deps.py")
        
        if not django_ok:
            print("\nPara configurar Django:")
            print("1. Verifica que sistema_medico/firebase_config.py existe")
            print("2. Verifica que sistema_medico/settings.py tiene la configuración de Firebase")

if __name__ == "__main__":
    main() 