from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from .models import Usuario
from django.contrib.auth.hashers import make_password
import re

# --- VISTA 1: Login (Autenticación Manual) ---
def login_view(request):
    if 'usuario_id' in request.session:
        return redirect('index')

    if request.method == 'POST':
        usuario_correo = request.POST.get('username').lower()
        contrasena = request.POST.get('password')    

        user = authenticate(request, username=usuario_correo, password=contrasena)

        if user is not None:
            request.session['usuario_id'] = user.pk 
            request.session['usuario_nombre'] = user.nombre
            
            messages.success(request, f"Bienvenido, {user.nombre}")
            return redirect('index')
        else:
            messages.error(request, "Credenciales inválidas (Correo o contraseña incorrectos)")
            return redirect('crear_usuario') 
    
    return redirect('crear_usuario')

# --- VISTA 2: Logout (Cerrar Sesión Manual) ---
def logout_view(request):
    request.session.flush() 
    
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('crear_usuario')


def index(request):
    # 1. Verificación de seguridad: ¿Existe la sesión?
    if 'usuario_id' not in request.session:
        messages.warning(request, "Debes iniciar sesión para ver esta página.")
        return redirect('crear_usuario') # Te manda al login si no hay sesión

    # 2. Recuperar datos del usuario
    usuario_id = request.session['usuario_id']
    
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        # Si el usuario fue borrado de la DB pero la cookie seguía viva
        request.session.flush()
        return redirect('crear_usuario')

    context = {
        'usuario': usuario
    }
    return render(request, 'index.html', context)


def crear_usuario(request):
    if 'usuario_id' in request.session:
        return redirect('index')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        mail = request.POST.get('mail').lower()
        contrasena = request.POST.get('contraseña')
        rol = request.POST.get('rol')
        
        patron_correo = r'^[a-zA-Z0-9._%+-]+@gmail.com$'

        # Validaciones
        if not mail or not nombre or not contrasena:
             messages.error(request, "Por favor completa todos los campos.")
             return redirect('crear_usuario')
        elif not re.match(patron_correo, mail):
            messages.error(request, "El formato del correo no es válido. Debe ser tipo ejemplo@gmail.com")
            return redirect('crear_usuario')
        elif len(contrasena) < 6:
            messages.error(request, "La contraseña debe tener al menos 6 caracteres.")
            return redirect('crear_usuario')
        elif Usuario.objects.filter(mail=mail).exists():
            messages.error(request, "Ya existe una cuenta con ese correo.")
            return redirect('crear_usuario')
        elif rol not in ['cliente', 'administrador']:
            messages.error(request, "El rol seleccionado no es válido.")
            return redirect('crear_usuario')

 
        # Guardar nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            mail=mail,
            contraseña=make_password(contrasena), 
            rol=rol
        )
        nuevo_usuario.save()

        messages.success(request, "Cuenta creada exitosamente. ¡Ahora inicia sesión!")
        return redirect('crear_usuario')

    # GET: Mostrar el HTML
    return render(request, 'crear_usuario.html')


def manejo(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']

    try:
        usuario_logueado = Usuario.objects.get(pk=usuario_id)
        if usuario_logueado.rol != 'administrador':
            return redirect('index')
        todos_los_usuarios = Usuario.objects.all() 
        context = {
            'usuario': usuario_logueado,
            'usuarios': todos_los_usuarios 
        }
        return render(request, 'manejo_usuario.html', context)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')


def editar_usuario(request, user_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')
    usuario_id = request.session['usuario_id']
    try:
        usuario_logueado = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')
    if usuario_logueado.rol != 'administrador':
        return redirect('index')
    try:
        usuario_obj = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('manejo')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        mail = request.POST.get('mail').lower() if request.POST.get('mail') else ''
        rol = request.POST.get('rol')
        patron_correo = r'^[a-zA-Z0-9._%+-]+@gmail.com$'
        
        
        if not nombre or not mail:
            messages.error(request, 'Nombre y mail son obligatorios.')
            return redirect('editar', user_id=user_id)
        elif Usuario.objects.filter(mail=mail).exclude(pk=usuario_obj.pk).exists():
            messages.error(request, 'El correo ya está en uso por otro usuario.')
            return redirect('editar', user_id=user_id)
        elif not re.match(patron_correo, mail):
            messages.error(request, 'El formato del correo no es válido. Debe ser tipo')
            return redirect('editar', user_id=user_id)
        
        usuario_obj.nombre = nombre
        usuario_obj.apellido = apellido
        usuario_obj.mail = mail
        if rol in ['cliente', 'administrador']:
            usuario_obj.rol = rol

        usuario_obj.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('manejo')

    # GET -> mostrar formulario
    context = {
        'usuario': usuario_logueado,
        'target': usuario_obj,
        'mode': 'editar'
    }
    return render(request, 'edicion_eliminacion.html', context)


def eliminar_usuario(request, user_id):
    # Requiere sesión y rol administrador
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']
    try:
        usuario_logueado = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

    if usuario_logueado.rol != 'administrador':
        return redirect('index')

    try:
        usuario_obj = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('manejo')

    if request.method == 'POST':
        # Confirm deletion
        usuario_obj.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('manejo')

    # GET -> mostrar confirmación
    context = {
        'usuario': usuario_logueado,
        'target': usuario_obj,
        'mode': 'eliminar'
    }
    return render(request, 'edicion_eliminacion.html', context)