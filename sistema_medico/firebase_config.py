import os
import firebase_admin
from firebase_admin import credentials, db
import pyrebase
from django.conf import settings

# Configuración de Firebase
FIREBASE_CONFIG = {
    'apiKey': os.environ.get('FIREBASE_API_KEY'),
    'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN'),
    'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
    'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
    'appId': os.environ.get('FIREBASE_APP_ID'),
    'databaseURL': os.environ.get('FIREBASE_DATABASE_URL'),
}

# Inicializar Firebase Admin SDK
def initialize_firebase():
    """Inicializa Firebase Admin SDK"""
    try:
        # Verificar si ya está inicializado
        firebase_admin.get_app()
        return firebase_admin.get_app()
    except ValueError:
        # Si no está inicializado, crear nueva instancia
        if os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY'):
            # Usar archivo de clave de servicio
            cred = credentials.Certificate(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY'))
        else:
            # Usar credenciales por defecto (para desarrollo local)
            cred = credentials.ApplicationDefault()
        
        return firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_CONFIG.get('databaseURL'),
            'storageBucket': FIREBASE_CONFIG.get('storageBucket')
        })

# Obtener instancia de Realtime Database
def get_database_client():
    """Obtiene el cliente de Realtime Database"""
    initialize_firebase()
    return db.reference()

# Obtener instancia de Pyrebase para operaciones más avanzadas
def get_pyrebase_client():
    """Obtiene el cliente de Pyrebase"""
    return pyrebase.initialize_app(FIREBASE_CONFIG)

# Configuración de nodos de la base de datos
DATABASE_NODES = {
    'usuarios': 'usuarios',
    'pacientes': 'pacientes',
    'signos_vitales': 'signos_vitales',
    'balance_hidrico': 'balance_hidrico',
    'evoluciones': 'evoluciones',
    'dispositivos': 'dispositivos',
    'cursos': 'cursos',
    'notificaciones': 'notificaciones',
    'configuraciones': 'configuraciones',
    'invitaciones': 'invitaciones',
} 