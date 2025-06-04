<<<<<<< HEAD
# TENS
proyecto para tens
=======
# Sistema Médico INACAP

Sistema de gestión de pacientes para la carrera de Técnico en Enfermería de INACAP. Esta aplicación permite a docentes y estudiantes gestionar pacientes, registrar signos vitales, balance hídrico, evoluciones clínicas y más.

## Requisitos previos

- Python 3.10 o superior
- pip (administrador de paquetes de Python)
- Virtualenv (recomendado)
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

## Configuración del entorno virtual

### Crear un entorno virtual

```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

### Activar el entorno virtual

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

## Configuración inicial

### Aplicar migraciones

```bash
python manage.py migrate
```

### Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en http://127.0.0.1:8000/

## Funcionalidades principales

- **Sistema de usuarios con roles**: Administradores, docentes y estudiantes
- **Gestión de cursos**: Creación y administración de cursos por docentes
- **Registro y gestión de pacientes**: Historial médico completo
- **Control de signos vitales**: Registro y visualización de signos vitales con gráficos
- **Registro de balance hídrico**: Control de ingresos y egresos de líquidos
- **Evoluciones clínicas**: Seguimiento detallado de la evolución del paciente
- **Dispositivos médicos**: Registro y seguimiento de dispositivos (sondas, vías, etc.)
- **Generación de fichas clínicas en PDF**: Reportes completos del paciente
- **Interfaz responsiva**: Diseño adaptable a dispositivos móviles y escritorio
- **Filtros y búsquedas avanzadas**: Localización rápida de información
- **Sistema de notificaciones**: Alertas para eventos importantes
- **Tema claro/oscuro**: Opciones de visualización para diferentes entornos

## Tecnologías utilizadas

- **Backend**: Django 5.1
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Base de datos**: SQLite (desarrollo), MySQL (producción)
- **Gráficos**: Chart.js
- **Reportes**: ReportLab
- **Componentes interactivos**: Flatpickr (calendarios mejorados)

## Estructura del proyecto

- **usuarios/**: Gestión de usuarios, autenticación y permisos
- **dashboard/**: Vistas principales del sistema
- **pacientes/**: Gestión de pacientes y sus datos
- **signos_vitales/**: Registro y visualización de signos vitales
- **balance_hidrico/**: Control de balance hídrico
- **evoluciones/**: Seguimiento de evoluciones clínicas
- **static/**: Archivos estáticos (CSS, JS, imágenes)
- **templates/**: Plantillas HTML

## Contribuciones

Para contribuir al proyecto:

1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b nueva-funcionalidad`)
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva funcionalidad'`)
4. Sube tus cambios a tu fork (`git push origin nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles. 
>>>>>>> 3332175 (Ocultar botones de acciones y registro para administrador)
