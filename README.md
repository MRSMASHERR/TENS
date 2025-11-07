# Sistema Médico INACAP

Sistema de gestión de pacientes para la carrera de Técnico en Enfermería de INACAP. Permite administrar usuarios, cursos, pacientes, signos vitales, balance hídrico y evoluciones.

## Requisitos

- Python 3.10+
- `pip`
- Entorno virtual (recomendado)

## Inicio rápido

```bash
# Crear y activar entorno virtual (Windows)
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tus valores locales

# Aplicar migraciones y ejecutar
python manage.py migrate
python manage.py runserver
```

El sistema quedará disponible en `http://127.0.0.1:8000/`.

## Variables de entorno

- `DJANGO_SECRET_KEY` — clave secreta de Django.
- `DEBUG` — `True` en local, `False` en producción.
- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` — dominios permitidos.
- `DATABASE_URL` — opcional en local; en Render se usa Postgres.
- `EMAIL_*` — configuración SMTP si deseas enviar correos.
- `ADMIN_*` o `DJANGO_SUPERUSER_*` — credenciales para crear superusuario automáticamente.

Consulta `.env.example` para una guía completa.

## Base de datos

- Desarrollo local: usa SQLite por defecto (`db.sqlite3`).
- Producción (Render): usar `DATABASE_URL` (PostgreSQL). En Render, copia el "Internal Database URL" del recurso de Postgres.

## Despliegue en Render (resumen)

- Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python init_render.py`
- Start: `gunicorn sistema_medico.wsgi:application`
- Variables: añade `DATABASE_URL` y las credenciales `ADMIN_*` o `DJANGO_SUPERUSER_*`.

Más detalles en `DEPLOYMENT.md`.

## Contribuciones

1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Haz commit (`git commit -m "feat: agrega funcionalidad"`).
4. Push y Pull Request.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
