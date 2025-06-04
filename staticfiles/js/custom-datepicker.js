/**
 * Mejora de los campos de fecha para hacerlos más amigables para el usuario
 * Utiliza flatpickr para una mejor experiencia de usuario
 */
document.addEventListener('DOMContentLoaded', function() {
    // Opciones globales para todos los datepickers
    const datepickerConfig = {
        locale: 'es',
        dateFormat: 'Y-m-d',
        altInput: true,
        altFormat: 'd/m/Y',
        disableMobile: false,
        allowInput: true,
        static: true,
        monthSelectorType: 'static',
        animate: true,
        nextArrow: '<i class="fas fa-chevron-right"></i>',
        prevArrow: '<i class="fas fa-chevron-left"></i>',
        showMonths: 1
    };

    // Configuración específica para fecha de nacimiento (no permite fechas futuras)
    const fechaNacimientoConfig = {
        ...datepickerConfig,
        maxDate: 'today',
        altFormat: 'd/m/Y (l)',
        onValueUpdate: function(selectedDates, dateStr, instance) {
            // Calcular la edad automáticamente
            const fechaNacimiento = new Date(dateStr);
            const edadMostrarInput = document.getElementById(instance.element.id.replace('fecha_nacimiento', 'edad_mostrar'));
            
            if (edadMostrarInput && !isNaN(fechaNacimiento.getTime())) {
                const hoy = new Date();
                let edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
                const m = hoy.getMonth() - fechaNacimiento.getMonth();
                
                // Si aún no ha llegado el cumpleaños de este año, restar un año
                if (m < 0 || (m === 0 && hoy.getDate() < fechaNacimiento.getDate())) {
                    edad--;
                }
                
                edadMostrarInput.value = edad;
            }
        }
    };

    // Configuración para rangos de fechas (inicio y fin)
    const rangoConfig = {
        ...datepickerConfig,
        defaultDate: 'today',
    };
    
    // Inicializar datepickers
    const inicializarDatepicker = () => {
        // Si flatpickr no está disponible, cargar la biblioteca
        if (typeof flatpickr === 'undefined') {
            // Cargar CSS de flatpickr
            const linkElement = document.createElement('link');
            linkElement.rel = 'stylesheet';
            linkElement.href = 'https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css';
            document.head.appendChild(linkElement);
            
            // Cargar tema
            const themeElement = document.createElement('link');
            themeElement.rel = 'stylesheet';
            themeElement.href = 'https://cdn.jsdelivr.net/npm/flatpickr/dist/themes/material_blue.css';
            document.head.appendChild(themeElement);
            
            // Cargar script de flatpickr
            const scriptElement = document.createElement('script');
            scriptElement.src = 'https://cdn.jsdelivr.net/npm/flatpickr';
            scriptElement.onload = function() {
                // Cargar localización en español
                const localeScript = document.createElement('script');
                localeScript.src = 'https://cdn.jsdelivr.net/npm/flatpickr/dist/l10n/es.js';
                localeScript.onload = function() {
                    // Una vez cargado todo, inicializar los datepickers
                    aplicarDatepickers();
                };
                document.head.appendChild(localeScript);
            };
            document.head.appendChild(scriptElement);
        } else {
            // Si ya está disponible, aplicar directamente
            aplicarDatepickers();
        }
    };
    
    // Función para aplicar los datepickers según su tipo
    const aplicarDatepickers = () => {
        // Todos los inputs de tipo date
        document.querySelectorAll('input[type="date"]').forEach(input => {
            // Detectar tipo de datepicker según su ID
            if (input.id.includes('fecha_nacimiento')) {
                flatpickr(input, fechaNacimientoConfig);
            } else if (input.id.includes('fecha_inicio') || input.id.includes('fecha_fin')) {
                // Configurar rangos de fechas (inicio y fin)
                flatpickr(input, rangoConfig);
            } else {
                // Configuración general para cualquier otro campo de fecha
                flatpickr(input, datepickerConfig);
            }
        });
    };
    
    // Iniciar el proceso
    inicializarDatepicker();
}); 