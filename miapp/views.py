from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages

from .models import Usuario


@login_required
def index(request):
    return render(request, 'index.html')


def CrearUsuario(request):
    if request.method == 'POST':

        # Obtener valores del formulario
        id_usuario = request.POST.get('id_usuario')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        mail = request.POST.get('mail')
        contraseña = request.POST.get('contraseña')
        rol = request.POST.get('rol')

        # Validar campos vacíos
        if not all([id_usuario, nombre, apellido, mail, contraseña, rol]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('login')

        # Comprobar si el usuario ya existe en Django
        if User.objects.filter(username=id_usuario).exists():
            messages.error(request, 'El ID de usuario (RUT) ya está registrado.')
            return redirect('login')

        try:
            # Crear usuario en Django Auth
            user_auth = User.objects.create_user(
                username=id_usuario,
                password=contraseña,
                first_name=nombre,
                last_name=apellido,
                email=mail,
                rol=rol
            )

            # Crear usuario en tu tabla Usuario
            user_bd = Usuario.objects.create(
                nombre=nombre,
                apellido=apellido,
                mail=mail,
                contraseña=contraseña,
                rol=rol
            )

            # Iniciar sesión
            login(request, user_auth)

            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('index')

        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {e}')
            return redirect('login')

    return redirect('login')