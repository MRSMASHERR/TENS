# Guía de Despliegue - Sistema Médico

## Problemas Identificados y Soluciones

### 1. Error 403 en Login (CSRF Verification Failed)

**Problema:** Los logs muestran errores 403 al intentar hacer login, lo que indica problemas de verificación CSRF.

**Causas:**
- Configuración de CSRF demasiado estricta para el entorno de producción
- Problemas con cookies seguras en HTTPS
- Middleware de CORS interfiriendo con CSRF

**Soluciones Aplicadas:**
- ✅ Configuración condicional de `CSRF_COOKIE_SECURE` y `SESSION_COOKIE_SECURE`
- ✅ Agregado soporte para HTTP y HTTPS en `CSRF_TRUSTED_ORIGINS`
- ✅ Configuración de CORS mejorada
- ✅ Removido middleware de debug en producción

### 2. Configuración de Seguridad

**Cambios Realizados:**
```python
# Antes
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Después
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
```

### 3. Variables de Entorno para Render

**Variables Requeridas:**
```bash
DJANGO_SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
USE_FIREBASE=False
ALLOWED_HOSTS=tens.onrender.com
CSRF_TRUSTED_ORIGINS=https://tens.onrender.com
CORS_ALLOWED_ORIGINS=https://tens.onrender.com
```

**Variables Opcionales para Superusuario:**
```bash
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@sistema-medico.com
ADMIN_PASSWORD=admin123456
```

## Pasos para Desplegar

### 1. Configurar Variables de Entorno en Render

1. Ve a tu dashboard de Render
2. Selecciona tu servicio web
3. Ve a "Environment"
4. Agrega las variables de entorno listadas arriba

### 2. Configurar Build Command

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python init_render.py
```

### 3. Configurar Start Command

```bash
gunicorn sistema_medico.wsgi:application
```

### 4. Verificar Despliegue

Después del despliegue, puedes verificar la configuración ejecutando:

```bash
python check_deployment.py
```

## Credenciales por Defecto

Si no configuras las variables de superusuario, se creará automáticamente con:

- **Usuario:** admin
- **Email:** admin@sistema-medico.com
- **Contraseña:** admin123456

**⚠️ IMPORTANTE:** Cambia la contraseña después del primer login.

## Troubleshooting

### Error 403 en Login

1. Verifica que las variables de entorno estén configuradas correctamente
2. Asegúrate de que `CSRF_TRUSTED_ORIGINS` incluya tu dominio
3. Verifica que `DEBUG=False` en producción

### No puedo ingresar con el superusuario en Render

1. Asegura que el dominio de tu servicio esté incluido en CSRF:
   - El proyecto ahora añade automáticamente `RENDER_EXTERNAL_HOSTNAME` a `CSRF_TRUSTED_ORIGINS`.
   - Revisa los logs de Render y confirma el hostname (ej. `tens-xxxxx.onrender.com`).
2. Resetea la contraseña del superusuario desde variables de entorno y reconstruye:
   - Define `DJANGO_SUPERUSER_USERNAME` y `DJANGO_SUPERUSER_PASSWORD` (o `ADMIN_USERNAME` / `ADMIN_PASSWORD`).
   - Durante el build, `init_render.py` actualizará la contraseña del superusuario existente.
3. Intenta ingresar usando:
   - Usuario: el `username` (por defecto `admin`).
   - Email: `admin@sistema-medico.com` (o el email que definiste).
   - El formulario acepta `email`, `RUT` o `username` en el campo usuario.

### Error de Archivos Estáticos

1. Verifica que `STATICFILES_STORAGE` esté configurado correctamente
2. Asegúrate de que `collectstatic` se ejecute durante el build

### Error de Base de Datos

1. Verifica que las migraciones se ejecuten correctamente
2. El proyecto usa SQLite por defecto; no requiere configuración de Firebase

## Monitoreo

### Logs Importantes a Revisar

1. **Errores 403:** Problemas de CSRF
2. **Errores 500:** Errores del servidor
3. **Errores de migración:** Problemas de base de datos
4. **Errores de archivos estáticos:** Problemas de configuración

### Comandos Útiles

```bash
# Verificar configuración
python check_deployment.py

# Crear superusuario durante el build
python init_render.py

# Ejecutar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

## Contacto

Si encuentras problemas adicionales, revisa:
1. Los logs de Render en tiempo real
2. La configuración de variables de entorno
3. La configuración de seguridad en `settings.py`