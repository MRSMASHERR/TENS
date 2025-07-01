# Migración a Firebase Realtime Database - Sistema Médico

Este documento contiene las instrucciones para migrar el sistema médico de MySQL/PostgreSQL a Firebase Realtime Database.

## Prerrequisitos

1. **Cuenta de Firebase**: Crear un proyecto en [Firebase Console](https://console.firebase.google.com/)
2. **Python 3.8+**: Asegúrate de tener Python instalado
3. **Dependencias**: Instalar las nuevas dependencias de Firebase

## Paso 1: Configurar Firebase

### 1.1 Crear proyecto en Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita Realtime Database
4. Habilita Authentication (si planeas usar autenticación de Firebase)
5. Habilita Storage (para archivos)

### 1.2 Obtener credenciales

1. En la consola de Firebase, ve a Configuración del proyecto
2. En la pestaña "Cuentas de servicio", descarga la clave privada
3. Guarda el archivo como `serviceAccountKey.json` en la raíz del proyecto

### 1.3 Configurar variables de entorno

Copia el archivo `firebase_env_example.txt` a `.env` y configura las variables:

```bash
cp firebase_env_example.txt .env
```

Edita el archivo `.env` con tus credenciales de Firebase:

```env
# Configuración de Firebase
FIREBASE_API_KEY=tu-api-key-de-firebase
FIREBASE_AUTH_DOMAIN=tu-proyecto.firebaseapp.com
FIREBASE_PROJECT_ID=tu-proyecto-id
FIREBASE_STORAGE_BUCKET=tu-proyecto.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abcdef123456
FIREBASE_DATABASE_URL=https://tu-proyecto-default-rtdb.firebaseio.com

# Ruta al archivo de clave de servicio de Firebase
FIREBASE_SERVICE_ACCOUNT_KEY=serviceAccountKey.json

# Configuración para usar Firebase como base de datos principal
USE_FIREBASE=False
```

## Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

## Paso 3: Migrar datos existentes

### 3.1 Ejecutar script de migración

```bash
python migrate_to_firebase.py
```

Este script:
- Migra todos los usuarios
- Migra todos los pacientes
- Migra todos los signos vitales
- Migra todos los balances hídricos
- Migra todas las evoluciones
- Migra todos los dispositivos
- Migra todas las notificaciones
- Migra todas las configuraciones
- Migra todas las invitaciones

### 3.2 Verificar migración

El script generará un archivo `firebase_migration_mapping.json` que contiene el mapeo de IDs entre la base de datos original y Firebase.

## Paso 4: Configurar Realtime Database

### 4.1 Reglas de seguridad

En la consola de Firebase, configura las reglas de Realtime Database:

```json
{
  "rules": {
    ".read": "auth != null",
    ".write": "auth != null",
    "usuarios": {
      "$uid": {
        ".read": "auth != null && (auth.uid == $uid || root.child('usuarios').child(auth.uid).child('rol').val() == 'administrador')",
        ".write": "auth != null && (auth.uid == $uid || root.child('usuarios').child(auth.uid).child('rol').val() == 'administrador')"
      }
    },
    "pacientes": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "signos_vitales": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "balance_hidrico": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "evoluciones": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

### 4.2 Índices

Realtime Database no requiere índices explícitos como Firestore, pero puedes optimizar las consultas organizando los datos de manera eficiente:

1. **Usuarios**: Organizar por `rut` como clave
2. **Pacientes**: Organizar por `rut` y `activo`
3. **Signos Vitales**: Organizar por `paciente_id` y `fecha_registro`
4. **Balance Hídrico**: Organizar por `paciente_id` y `fecha`
5. **Evoluciones**: Organizar por `paciente_id` y `fecha`

## Paso 5: Activar Firebase

### 5.1 Cambiar configuración

Una vez que la migración esté completa, cambia la variable de entorno:

```env
USE_FIREBASE=True
```

### 5.2 Reiniciar aplicación

```bash
python manage.py runserver
```

## Paso 6: Verificar funcionamiento

### 6.1 Probar funcionalidades básicas

1. **Login de usuarios**: Verificar que los usuarios puedan iniciar sesión
2. **Lista de pacientes**: Verificar que se muestren los pacientes migrados
3. **Registro de datos**: Verificar que se puedan crear nuevos registros
4. **Consultas**: Verificar que las búsquedas funcionen correctamente

### 6.2 Monitorear Realtime Database

En la consola de Firebase, verifica que:
- Los datos se estén guardando correctamente
- Las consultas sean eficientes
- No haya errores de permisos

## Estructura de datos en Realtime Database

### Nodos principales

1. **usuarios**: Información de usuarios del sistema
2. **pacientes**: Datos de pacientes
3. **signos_vitales**: Registros de signos vitales
4. **balance_hidrico**: Registros de balance hídrico
5. **evoluciones**: Evoluciones de pacientes
6. **dispositivos**: Dispositivos médicos
7. **cursos**: Cursos académicos
8. **notificaciones**: Notificaciones del sistema
9. **configuraciones**: Configuraciones de usuario
10. **invitaciones**: Invitaciones a cursos

### Estructura de registros

Cada registro incluye:
- `id`: ID único del registro
- `created_at`: Fecha de creación
- `updated_at`: Fecha de última actualización
- Campos específicos del modelo

## Solución de problemas

### Error de autenticación

```bash
# Verificar que el archivo de clave de servicio existe
ls -la serviceAccountKey.json

# Verificar variables de entorno
echo $FIREBASE_SERVICE_ACCOUNT_KEY
```

### Error de permisos

1. Verificar las reglas de Firestore
2. Asegurar que el usuario tenga permisos adecuados
3. Verificar que la clave de servicio tenga permisos de administrador

### Datos no migrados

1. Revisar el archivo `firebase_migration_mapping.json`
2. Ejecutar el script de migración nuevamente
3. Verificar logs de errores

## Ventajas de Firebase

1. **Escalabilidad**: Se adapta automáticamente al crecimiento
2. **Tiempo real**: Actualizaciones en tiempo real
3. **Seguridad**: Reglas de seguridad granulares
4. **Backup automático**: Copias de seguridad automáticas
5. **Integración**: Fácil integración con otros servicios de Google Cloud

## Consideraciones importantes

1. **Costos**: Firebase tiene costos por uso, revisa la facturación
2. **Latencia**: Puede haber latencia en consultas complejas
3. **Limitaciones**: Algunas consultas complejas pueden requerir índices
4. **Migración**: Mantén la base de datos original como respaldo

## Soporte

Si encuentras problemas durante la migración:

1. Revisa los logs de Django
2. Verifica la consola de Firebase
3. Consulta la documentación oficial de Firebase
4. Revisa el archivo de mapeo de IDs generado 