from functools import wraps
from django.shortcuts import redirect
from .models import Usuario

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):

        # Seguridad: validar sesión existente
        if 'usuario_id' not in request.session:
            return redirect('crear_usuario')

        usuario = Usuario.objects.get(pk=request.session['usuario_id'])

        # Control de rol
        if usuario.rol != 'administrador':
            return redirect('index')

        return view_func(request, *args, **kwargs)

    return _wrapped

def owner_required(model, field):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):

            # Validar sesión
            if 'id_usuario' not in request.session:
                return redirect('crear_usuario')

            usuario = Usuario.objects.get(pk=request.session['usuario_id'])

            # Obtener objeto (anti-IDOR)
            try:
                obj = model.objects.get(pk=kwargs[field])
            except model.DoesNotExist:
                return redirect('index')

            # Validar propiedad o rol admin
            if usuario.rol != 'administrador' and obj.id_usuario != usuario:
                return redirect('index')

            return view_func(request, *args, **kwargs)

        return _wrapped
    return decorator

def login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):

        # Validar sesión existente
        if 'usuario_id' not in request.session:
            return redirect('crear_usuario')

        return view_func(request, *args, **kwargs)

    return _wrapped