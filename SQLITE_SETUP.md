# Configuración SQLite para Render

## 🎯 **Objetivo**
Configurar el Sistema Médico para usar SQLite en Render, evitando problemas de conexión a PostgreSQL.

## ✅ **Cambios Realizados**

### 1. **Configuración de Base de Datos Simplificada**
- ✅ Eliminada dependencia de PostgreSQL
- ✅ SQLite configurado para desarrollo y producción
- ✅ Removidas dependencias innecesarias (`dj-database-url`, `psycopg2-binary`)

### 2. **Scripts de Configuración**
- ✅ `setup_sqlite.py` - Script simplificado para Render
- ✅ `render_sqlite_final.yaml` - Configuración completa para Render

## 🚀 **Configuración en Render**

### **Paso 1: Variables de Entorno**

Ve a tu dashboard de Render → Environment y configura estas variables:

```bash
# Configuración básica
DJANGO_SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=tens.onrender.com

# Seguridad
CSRF_TRUSTED_ORIGINS=https://tens.onrender.com
CORS_ALLOWED_ORIGINS=https://tens.onrender.com

# Firebase
USE_FIREBASE=True
FIREBASE_API_KEY=AIzaSyAS4T6gfkIw0lgN6lrvvDBI-qr8_Eih_hA
FIREBASE_AUTH_DOMAIN=tens-4e985.firebaseapp.com
FIREBASE_PROJECT_ID=tens-4e985
FIREBASE_STORAGE_BUCKET=tens-4e985.appspot.com
FIREBASE_MESSAGING_SENDER_ID=170026841030
FIREBASE_DATABASE_URL=https://tens-4e985-default-rtdb.firebaseio.com

# Superusuario
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@sistema-medico.com
ADMIN_PASSWORD=admin123456

# Archivos estáticos
STATICFILES_STORAGE=whitenoise.storage.CompressedManifestStaticFilesStorage
```

### **Paso 2: Build Command**

Cambia tu build command a:
```bash
pip install -r requirements.txt && python setup_sqlite.py
```

### **Paso 3: Start Command**

Mantén el start command como:
```bash
gunicorn sistema_medico.wsgi:application
```

## 🔧 **Eliminar Variables Problemáticas**

**IMPORTANTE:** Elimina estas variables si las tienes en Render:
- ❌ `DATABASE_URL` (causa problemas de conexión)
- ❌ `FORCE_SQLITE` (ya no es necesaria)

## 📊 **Ventajas de SQLite en Render**

1. **Simplicidad:** No requiere configuración de base de datos externa
2. **Confiabilidad:** Menos puntos de falla
3. **Rendimiento:** Adecuado para aplicaciones pequeñas y medianas
4. **Costo:** Gratuito, no requiere servicio de base de datos

## ⚠️ **Limitaciones de SQLite**

1. **Concurrencia:** Limitado para múltiples escrituras simultáneas
2. **Escalabilidad:** No es ideal para aplicaciones muy grandes
3. **Persistencia:** Los datos se reinician en cada deploy (en el plan gratuito)

## 🎉 **Resultado Esperado**

Después de la configuración:
- ✅ Aplicación funcionando en `https://tens.onrender.com`
- ✅ Login funcionando sin errores 403
- ✅ Admin panel accesible
- ✅ Superusuario creado automáticamente

## 🔍 **Verificación**

Para verificar que todo funciona:

1. **Accede a:** `https://tens.onrender.com/usuarios/login/`
2. **Credenciales:** `admin` / `admin123456`
3. **Admin:** `https://tens.onrender.com/admin/`

## 🆘 **Solución de Problemas**

### Error de Migraciones
Si hay problemas con las migraciones, el script `setup_sqlite.py` incluye manejo de errores.

### Error de Archivos Estáticos
Verifica que `STATICFILES_STORAGE` esté configurado correctamente.

### Error de CSRF
Asegúrate de que `CSRF_TRUSTED_ORIGINS` incluya tu dominio.

## 📞 **Soporte**

Si encuentras problemas:
1. Revisa los logs de Render
2. Verifica las variables de entorno
3. Asegúrate de que no haya variables `DATABASE_URL` configuradas 