from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from .models import Usuario
import re

# --- VISTA 1: Login (Autenticación Manual) ---
def login_view(request):
    # Si ya está logueado, no tiene sentido ver el login, lo mandamos al inicio
    if 'usuario_id' in request.session:
        return redirect('index')

    if request.method == 'POST':
        # Django envía el input name="username" (tu correo) en este campo
        usuario_correo = request.POST.get('username').lower()
        contrasena = request.POST.get('password')    

        # 1. Tu backends.py verifica si el correo existe y la contraseña coincide
        user = authenticate(request, username=usuario_correo, password=contrasena)

        if user is not None:
            # 2. CREAR LA SESIÓN MANUALMENTE
            # Guardamos el ID en la sesión. NO usamos login() para evitar error de last_login
            request.session['usuario_id'] = user.pk 
            request.session['usuario_nombre'] = user.nombre
            
            messages.success(request, f"Bienvenido, {user.nombre}")
            return redirect('index') # Al 'name' que definimos en urls.py para el inicio
        else:
            messages.error(request, "Credenciales inválidas (Correo o contraseña incorrectos)")
            # Si falla, volvemos a la pantalla de login
            return redirect('crear_usuario') 
    
    # Si intentan entrar por GET a /login/, los mandamos al formulario
    return redirect('crear_usuario')

# --- VISTA 2: Logout (Cerrar Sesión Manual) ---
def logout_view(request):
    # Borramos TODOS los datos de la sesión (id, nombre, cookies, etc.)
    request.session.flush() 
    
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('crear_usuario')

# --- VISTA 3: Página Principal (Protegida Manualmente) ---
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

# --- VISTA 4: Registro y Pantalla de Login ---
def crear_usuario(request):
    if 'usuario_id' in request.session:
        return redirect('index')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        mail = request.POST.get('mail').lower()
        contrasena = request.POST.get('contraseña')
        rol = request.POST.get('rol')

        # Validaciones
        if not mail or not nombre or not contrasena:
             messages.error(request, "Por favor completa todos los campos.")
             return redirect('crear_usuario')

        # 2. Validar FORMATO de correo (algo@algo.com)
        patron_correo = r'^[a-zA-Z0-9._%+-]+@[gmail.]+\.[com]{2,}$'
        
        if not re.match(patron_correo, mail):
            messages.error(request, "El formato del correo no es válido. Debe ser tipo ejemplo@gmail.com")
            return redirect('crear_usuario')


        # Guardar nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            mail=mail,
            contraseña=contrasena, 
            rol=rol
        )
        nuevo_usuario.save()

        messages.success(request, "Cuenta creada exitosamente. ¡Ahora inicia sesión!")
        return redirect('crear_usuario')

    # GET: Mostrar el HTML
    return render(request, 'crear_usuario.html')