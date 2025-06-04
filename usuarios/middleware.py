from .models import ConfiguracionUsuario

class ConfiguracionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Obtener o crear la configuración del usuario
            config = ConfiguracionUsuario.objects.get_or_create(usuario=request.user)[0]
            
            # Actualizar el tema en la sesión si:
            # 1. No existe en la sesión
            # 2. Es diferente al valor en la configuración
            if 'tema_oscuro' not in request.session or request.session['tema_oscuro'] != config.tema_oscuro:
                request.session['tema_oscuro'] = config.tema_oscuro
                # Forzar guardado de la sesión
                request.session.modified = True
        
        response = self.get_response(request)
        return response 