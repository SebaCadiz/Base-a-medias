from django.contrib.auth.backends import BaseBackend
from .models import Usuario  

class UsuarioBackend(BaseBackend):
    """
    Autentica usuarios buscando por su CORREO (mail) en lugar de su nombre.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            usuario = Usuario.objects.get(mail=username)
        except Usuario.DoesNotExist:
            return None # No existe ese correo

        # Verificamos la contraseña (texto plano según tu configuración actual)
        if usuario.contraseña == password:
            return usuario
        else:
            return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None