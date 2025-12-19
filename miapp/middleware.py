from django.shortcuts import redirect
from django.urls import resolve

RUTAS_PUBLICAS = [
    'crear_usuario',
    'login',
    'logout',
    'registro',
]

class AccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resolver = resolve(request.path_info)
        nombre_vista = resolver.url_name

        # Permitir archivos estáticos
        if request.path.startswith('/static/'):
            return self.get_response(request)

        # Permitir vistas públicas
        if nombre_vista in RUTAS_PUBLICAS:
            return self.get_response(request)

        # Bloquear todo lo demás
        if 'usuario_id' not in request.session:
            return redirect('crear_usuario')

        return self.get_response(request)
    
class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "  # 'unsafe-inline' permite scripts en el HTML 
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "               # data: permite imágenes en base64
            "font-src 'self'; "
            "object-src 'none'; "                  # Bloquea plugins como Flash
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        response['Content-Security-Policy'] = csp_policy
        return response