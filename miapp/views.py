from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from .models import Usuario, ClasificacionTributaria, Contribuyente, Pais,Evento
from .pulsar_nuam import publicar_evento
from .models import Evento
from .services.exchange import convert_currency, list_currencies,get_mock_chart_data
from django.db import transaction
from datetime import date , timedelta
import pandas as pd
import re
import time 
from django.core.cache import cache
from .decorators import admin_required
from django.views.decorators.cache import never_cache



# ----------------------------
# CONFIGURACIONES GENERALES
# ----------------------------

CONTRASENAS_PROHIBIDAS = [
    "123456", "password", "qwerty", "admin", "12345678",
    "123456789", "abc123", "clave", "111111", "000000"
]

MAX_FALLOS = 3
BLOQUEO_TIEMPO = 60 * 30
PATRON_LISTA = r'^[a-zA-Z0-9\s.,\-#/ñÑáéíóúÁÉÍÓÚ]*$'
patron_correo = r'^[a-zA-Z0-9._%+-]+@gmail.com$'
DIAS_ROTACION_CONTRASENA = 90
validar_password = lambda pwd: (len(pwd) >= 6 and
                              pwd not in CONTRASENAS_PROHIBIDAS and
                              re.search(r'[A-Z]', pwd) and
                              re.search(r'[a-z]', pwd) and
                              re.search(r'[0-9]', pwd)
                             )

def get_failure_key(email):
    return f'login_fail:{email}'

def get_last_password_change_date(usuario_id):
    EVENTOS_RELEVANTES = ['USUARIO CREADO', 'ROTACIÓN DE CONTRASEÑA']
    try:
        latest_event = Evento.objects.filter(
            tipo__in=EVENTOS_RELEVANTES, 
            contenido__usuario_id=usuario_id 
        ).order_by('-timestamp').first()

        if not latest_event:
             latest_event = Evento.objects.filter(
                tipo__in=EVENTOS_RELEVANTES, 
                contenido__id=usuario_id 
            ).order_by('-timestamp').first()
        if latest_event:
            return latest_event.timestamp.date()    
    except Exception:
        pass
    return date.today()
        
# ----------------------------
# LOGIN / LOGOUT
# ----------------------------


def login_view(request):
    # ... (código inicial de redirección y POST) ...
    if 'usuario_id' in request.session:
        return redirect('index')

    if request.method == 'POST':
        usuario_correo = request.POST.get('username', '').lower().strip()
        contrasena = request.POST.get('password', '')

        # ... (código de last_login_attempt_email y validación de campos vacíos) ...
        request.session['last_login_attempt_email'] = usuario_correo

        if not usuario_correo or not contrasena:
            messages.error(request, "Por favor, ingresa correo y contraseña.")
            return redirect('crear_usuario')

        key = get_failure_key(usuario_correo)
        MAX_FALLOS = 3 # Revisa que esta constante esté accesible o defínela aquí
        BLOQUEO_TIEMPO = 60 * 30 # Revisa que esta constante esté accesible o defínela aquí

        fallos_consecutivos = cache.get(key, 0)

        # 🔒 1. VERIFICAR BLOQUEO ANTES DE AUTENTICAR
        if fallos_consecutivos >= MAX_FALLOS:
            # Si el contador ya alcanzó o superó el límite, BLOQUEAR INMEDIATAMENTE.
            messages.error(
                request,
                "⚠️ Cuenta bloqueada temporalmente por demasiados intentos fallidos. Intenta de nuevo en 30 minutos."
            )
            time.sleep(2)
            return redirect('crear_usuario')
        
        # 2. INTENTAR AUTENTICACIÓN
        # PREVENCIÓN: Verificar si existen múltiples usuarios con el mismo mail
        usuarios_coincidentes = Usuario.objects.filter(mail=usuario_correo)
        if usuarios_coincidentes.count() > 1:
            # Evitar que el backend falle con MultipleObjectsReturned
            messages.error(
                request,
                "Existe más de una cuenta registrada con ese correo. Contacta a soporte para fusionar cuentas."
            )
            return redirect('crear_usuario')

        user = authenticate(request, username=usuario_correo, password=contrasena)

        if user is not None:
            # ✅ Login correcto → reset contador
            cache.delete(key)
            request.session.cycle_key()
            request.session['usuario_id'] = user.pk
            request.session['usuario_nombre'] = user.nombre
            request.session.pop('last_login_attempt_email', None)

            messages.success(request, f"Bienvenido, {user.nombre}")
            return redirect('index')

        # 3. ❌ Login fallido → incrementar y verificar si se alcanzó el bloqueo.
        fallos_consecutivos += 1
        
        if fallos_consecutivos >= MAX_FALLOS:
            # Bloquear la cuenta justo en el intento que alcanzó el límite
            # El timeout asegura que el bloqueo dure lo que diga BLOQUEO_TIEMPO
            cache.set(key, fallos_consecutivos, timeout=BLOQUEO_TIEMPO)
            messages.error(
                request,
                f"Credenciales inválidas. ¡Tu cuenta ha sido bloqueada temporalmente! Intenta de nuevo en {int(BLOQUEO_TIEMPO / 60)} minutos."
            )
        else:
            # Simplemente actualizar el contador sin cambiar el timeout (se usa el timeout por defecto si se usó)
            cache.set(key, fallos_consecutivos, timeout=BLOQUEO_TIEMPO)
            messages.error(request, "Credenciales inválidas (Correo o contraseña incorrectos)")


        time.sleep(1)
        return redirect('crear_usuario')

    return redirect('crear_usuario')  

def logout_view(request):
    request.session.flush() 
    return redirect('crear_usuario')


# ----------------------------
# HOME
# ----------------------------

def index(request):
    if 'usuario_id' not in request.session:
        messages.warning(request, "Debes iniciar sesión para ver esta página.")
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']
    
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
        fecha_ultimo_cambio = get_last_password_change_date(usuario.pk)
        fecha_limite = fecha_ultimo_cambio + timedelta(days=DIAS_ROTACION_CONTRASENA)   
        if date.today() >= fecha_limite:
            tiempo_transcurrido = (date.today() - fecha_ultimo_cambio).days
            messages.warning(request, f"⚠️ Tu contraseña ha expirado. Han pasado {tiempo_transcurrido} días. Debes cambiarla para continuar.")
            return redirect('configurar_cuenta') # Redirige para forzar el cambio
            
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

    return render(request, 'Index.html', {'usuario': usuario})


# ----------------------------
# USUARIOS
# ----------------------------
# En views.py

def crear_usuario(request):
    if 'usuario_id' in request.session:
        return redirect('index')

    if request.method == 'POST':
        # 1. Obtener valores sin procesar la variable 'mail' de inmediato.
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        mail_raw = request.POST.get('mail')  # Obtenemos el mail sin .lower()
        contrasena = request.POST.get('contraseña')
        rol = request.POST.get('rol')
        # 2. VALIDAR CAMPOS VACÍOS
        if not mail_raw or not nombre or not apellido or not contrasena or not rol:
            messages.error(request, "Por favor completa todos los campos.")
            return redirect('crear_usuario')
        mail = mail_raw.lower().strip()  # Ahora sí procesamos mail 
        if not re.match(patron_correo, mail):
            messages.error(request, "El formato del correo no es válido. Debe ser tipo ejemplo@gmail.com")
            return redirect('crear_usuario')

        if not validar_password(contrasena):
            messages.error(request, "La contraseña es demasiado débil. Debe tener al menos 6 caracteres, incluir mayúsculas, minúsculas y números, y no ser una contraseña común.")
            return redirect('crear_usuario')

        if Usuario.objects.filter(mail=mail).exists():
            messages.error(request, "Ya existe una cuenta con ese correo.")
            return redirect('crear_usuario')

        if rol not in ['cliente', 'administrador']:
            messages.error(request, "El rol seleccionado no es válido.")
            return redirect('crear_usuario')

        # 3. CREACIÓN DEL USUARIO (con manejo de excepciones para la base de datos)
        try:
            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                mail=mail,
                contraseña=make_password(contrasena), 
                rol=rol
            )
            try:
                nuevo_usuario.save()
            except Exception as e:
                print(f"Error interno al guardar el usuario: {e}")
                messages.error(request, f"Error")
                return redirect('crear_usuario')
            # 4. ESTABLECER EL MENSAJE DE ÉXITO PRIMERO (Aislamiento de Pulsar)
            messages.success(request, "Cuenta creada exitosamente. ¡Ahora inicia sesión!")

            # 5. Intentar la publicación de Pulsar
            try:
                publicar_evento('USUARIO CREADO', {
                    'usuario_id': nuevo_usuario.id_usuario,
                    'nombre': nuevo_usuario.nombre,
                    'mail': nuevo_usuario.mail,
                    'rol': nuevo_usuario.rol
                })
                
            except Exception as pulsar_e:
                # Si Pulsar falla, el mensaje de éxito ya fue establecido.
                # Imprimimos el error en la consola para depuración, pero continuamos.
                print(f"ERROR PULSAR (USUARIO ID: {nuevo_usuario.id_usuario}): {pulsar_e}")
                
        except Exception as db_e:
            # Captura cualquier error de base de datos o fallo inesperado
            messages.error(request, f"Error interno al guardar el usuario: {db_e}")
            print(f"ERROR AL GUARDAR USUARIO: {db_e}")

        # La redirección se ejecuta SIEMPRE al final del POST.
        return redirect('crear_usuario')

    return render(request, 'crear_usuario.html')


@admin_required
def manejo(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']

    try:
        usuario_logueado = Usuario.objects.get(pk=usuario_id)
        if usuario_logueado.rol != 'administrador':
            return redirect('index')

        todos_los_usuarios = Usuario.objects.all() 

        return render(request, 'manejo_usuario.html', {
            'usuario': usuario_logueado,
            'usuarios': todos_los_usuarios 
        })

    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')
 
def configurar_cuenta(request):
    # Validar sesión
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        mail = request.POST.get('mail').lower().strip()

        # Cambio contraseña
        current_pass = request.POST.get('password_current')
        new_pass = request.POST.get('password_new')
        confirm_pass = request.POST.get('password_confirm')


        # Validar contraseña actual
        if new_pass or confirm_pass:
            

            if new_pass != confirm_pass:
                messages.error(request, "Las nuevas contraseñas no coinciden.")
                return render(request, 'cuenta.html', {'usuario': usuario})

            if not validar_password(new_pass):
                messages.error(request, "La nueva contraseña es demasiado débil.")
                return render(request, 'cuenta.html', {'usuario': usuario})

            usuario.set_password(new_pass)

        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.mail = mail
        usuario.save()

        messages.success(request, "Perfil actualizado exitosamente.")
        usuario.save()

        publicar_evento('USUARIO DE ACTUALIZADO', {
                'id': usuario.id_usuario,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'mail': usuario.mail
            })
            
            # Actualizar nombre en sesión
        request.session['usuario_nombre'] = usuario.nombre
    return render(request, 'cuenta.html', {'usuario': usuario})



def eliminar_cuenta(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')
    
    if request.method == 'POST':
        usuario_id = request.session['usuario_id']
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            
            # ✅ Publicar evento UNA SOLA VEZ antes de eliminar
            try:
                publicar_evento('ELIMINAR USUARIO', {
                    'id': usuario.id_usuario,
                    'nombre': usuario.nombre,
                    'apellido': usuario.apellido,
                    'mail': usuario.mail,
                    'rol': usuario.rol
                })
            except Exception as pulsar_e:
                print(f"ERROR PULSAR AL ELIMINAR USUARIO: {pulsar_e}")
            
            usuario.delete()
            request.session.flush()
            messages.success(request, "Tu cuenta ha sido eliminada permanentemente.")
            return redirect('crear_usuario') 
        
        except Usuario.DoesNotExist:
            request.session.flush()
            return redirect('crear_usuario')

    # Si intentan entrar por URL directa sin usar el botón (GET), los devolvemos
    return redirect('cuenta')

@admin_required
def usuarios_contribuyentes(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')


    try:
        admin = Usuario.objects.get(pk=request.session['usuario_id'])
        usuarios = Usuario.objects.all().order_by('id_usuario')
        usuarios_contribs = []

        for u in usuarios:
            contribs = Contribuyente.objects.filter(id_usuario=u)
            usuarios_contribs.append({'usuario': u, 'contribuyentes': contribs})

        return render(request, 'usuarios_contribuyentes.html', {
            'usuario': admin,
            'usuarios_contribs': usuarios_contribs
        })

    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

@admin_required
def editar_usuario(request, user_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')
    usuario_id = request.session['usuario_id']
    try:
        usuario_logueado = Usuario.objects.get(pk=usuario_id)
        
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')
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
        # Validaciones
        if not nombre or not mail:
            messages.error(request, 'Nombre y mail son obligatorios.')
            return redirect('editar', user_id=user_id)
        if Usuario.objects.filter(mail=mail).exclude(pk=usuario_obj.pk).exists():
            messages.error(request, 'El correo ya está en uso por otro usuario.')
            return redirect('editar', user_id=user_id)

        if not re.match(patron_correo, mail):
            messages.error(request, 'El formato del correo no es válido.')
            return redirect('editar', user_id=user_id)
        # Actualizar
        usuario_obj.nombre = nombre
        usuario_obj.apellido = apellido
        usuario_obj.mail = mail       
        if rol in ['cliente', 'administrador']:
            usuario_obj.rol = rol
        usuario_obj.save()

        publicar_evento('EDITAR USUARIO', {
            'id': usuario_obj.id_usuario,
            'nombre': usuario_obj.nombre,
            'apellido': usuario_obj.apellido,
            'mail': usuario_obj.mail,
            'rol': usuario_obj.rol
        })
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('manejo')
    return render(request, 'edicion_eliminacion.html', {
        'usuario': usuario_logueado,
        'target': usuario_obj,
        'mode': 'editar'
    })
    
@admin_required
def eliminar_usuario(request, user_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')
    usuario_id = request.session['usuario_id']
    try:
        usuario_logueado = Usuario.objects.get(pk=usuario_id)
        if usuario_logueado.rol != 'administrador':
            return redirect('index')
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')
    try:
        usuario_obj = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuario no encontrado.')
        return redirect('manejo')
    if request.method == 'POST':
        # 🔥 PUBLICAR ANTES DE BORRAR (para enviar los datos)
        publicar_evento('ELIMINAR USUARIO', {
            'id': usuario_obj.id_usuario,
            'nombre': usuario_obj.nombre,
            'apellido': usuario_obj.apellido,
            'mail': usuario_obj.mail,
            'rol': usuario_obj.rol
        })
        usuario_obj.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('manejo')
    return render(request, 'edicion_eliminacion.html', {
        'usuario': usuario_logueado,
        'target': usuario_obj,
        'mode': 'eliminar'
    })


# ----------------------------
# CONTRIBUYENTES
# ----------------------------

TIPO_CONTRIBUYENTE_CHOICES = {
    'Jurídica': 'Jurídica',
    'Natural': 'Natural'
}
def manejo_tributarios(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')
    usuario_id = request.session['usuario_id']
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
        contribuyentes = Contribuyente.objects.filter(id_usuario=usuario)
        paises = Pais.objects.all()
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')
    
    return render(request, 'manejo_tributarios.html', {
        'usuario': usuario,
        'contribuyentes': contribuyentes,
        'paises': paises,
        'tipos_contribuyente': TIPO_CONTRIBUYENTE_CHOICES.items(),
        'situacion_choices': ['Activo', 'Inactivo']
    })


def crear_contribuyente(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')
    
    usuario_id = request.session['usuario_id']

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')
    
    if request.method == 'POST':
        try:
            id_pais = request.POST.get('id_pais')
            tipo = request.POST.get('tipo')
            situacion = request.POST.get('situacion')
            nombre_comercial = request.POST.get('nombre_comercial')
            actividad_economica = request.POST.get('actividad_economica')
            identificador_tributario = request.POST.get('identificador_tributario')
            categoria = request.POST.get('categoria')
            empleados_str = (request.POST.get('empleados') or '').strip()

            # Requerir empleados si la naturaleza es Jurídica
            if tipo == 'Jurídica' and not empleados_str:
                messages.error(request, 'El número de empleados es obligatorio para contribuyentes de naturaleza Jurídica.')
                return redirect('manejo_tributarios')

            empleados = int(empleados_str) if empleados_str.isdigit() else 0

            pais = Pais.objects.get(pk=id_pais)
            contribuyente = Contribuyente(
                id_usuario=usuario,
                id_pais=pais,
                tipo=tipo,
                situación=situacion,
                nombre_comercial=nombre_comercial,
                actividad_economica=actividad_economica,
                identificador_tributario=identificador_tributario,
                empleados=empleados,
                categoria = categoria
            )
            contribuyente.save()

            messages.success(request, f'Contribuyente "{nombre_comercial}" creado exitosamente.')

            publicar_evento('CONTRIBUYENTE CREADO', {
                'nombre_comercial': contribuyente.nombre_comercial,
                'usuario': usuario.mail,
                'pais': pais.pais_nom
            })

            return redirect('manejo_tributarios')
        
        except Pais.DoesNotExist:
            messages.error(request, 'País seleccionado inválido.')
        except Exception as e:
            print(f'Error al crear contribuyente: {e}')
            messages.error(request, f'Error')

        return redirect('manejo_tributarios')
    
    return redirect('manejo_tributarios')

def editar_tributario(request, contribuyente_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']
    usuario = Usuario.objects.get(pk=usuario_id)

    try:
        contribuyente = Contribuyente.objects.get(pk=contribuyente_id)
    except Contribuyente.DoesNotExist:
        messages.error(request, 'Contribuyente no encontrado.')
        return redirect('manejo_tributarios')

    if usuario.rol != 'administrador' and contribuyente.id_usuario != usuario:
        messages.error(request, "No autorizado.")
        return redirect('manejo_tributarios')

    if request.method == 'POST':
        try:
            new_tipo = request.POST.get('tipo')
            contribuyente.tipo = new_tipo
            contribuyente.situación = request.POST.get('situacion')
            contribuyente.nombre_comercial = request.POST.get('nombre_comercial')
            contribuyente.actividad_economica = request.POST.get('actividad_economica')
            contribuyente.identificador_tributario = request.POST.get('identificador_tributario')

            empleados_str = (request.POST.get('empleados') or '').strip()

            # Requerir empleados si la naturaleza es Jurídica
            if new_tipo == 'Jurídica' and not empleados_str:
                messages.error(request, 'El número de empleados es obligatorio para contribuyentes de naturaleza Jurídica.')
                return redirect('editar_tributario', contribuyente_id=contribuyente_id)

            contribuyente.empleados = int(empleados_str) if empleados_str and empleados_str.isdigit() else 0

            contribuyente.save()

            messages.success(request, 'Contribuyente actualizado correctamente.')
            return redirect('manejo_tributarios')

        except Exception as e:
            print(f'Error al actualizar contribuyente: {e}')
            messages.error(request, f'Error al actualizar')

    return render(request, 'editar_tributario.html', {
        'usuario': usuario,
        'contribuyente': contribuyente,
        'tipos_contribuyente': TIPO_CONTRIBUYENTE_CHOICES.items(),
        'situacion_choices': ['Activo', 'Inactivo'],
        'mode': 'editar'
    })
def eliminar_tributario(request, contribuyente_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']
    usuario = Usuario.objects.get(pk=usuario_id)

    try:
        contribuyente = Contribuyente.objects.get(pk=contribuyente_id)
    except Contribuyente.DoesNotExist:
        messages.error(request, 'Contribuyente no encontrado.')
        return redirect('manejo_tributarios')

    if usuario.rol != 'administrador' and contribuyente.id_usuario != usuario:
        messages.error(request, "No autorizado.")
        return redirect('manejo_tributarios')

    if request.method == 'POST':
        contribuyente.delete()
        messages.success(request, 'Contribuyente eliminado exitosamente.')
        return redirect('manejo_tributarios')

    return render(request, 'editar_tributario.html', {
        'usuario': usuario,
        'contribuyente': contribuyente,
        'tipos_contribuyente': TIPO_CONTRIBUYENTE_CHOICES.items(),
        'mode': 'eliminar'
    })


# ----------------------------
# CLASIFICACIONES TRIBUTARIAS
# ----------------------------
def clasificaciones_por_contribuyente(request, contribuyente_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']
    usuario = Usuario.objects.get(pk=usuario_id)

    try:
        contribuyente = Contribuyente.objects.get(pk=contribuyente_id)
    except Contribuyente.DoesNotExist:
        messages.error(request, "Contribuyente no encontrado.")
        return redirect('manejo_tributarios')

    if usuario.rol != 'administrador' and contribuyente.id_usuario != usuario:
        messages.error(request, "No autorizado.")
        return redirect('manejo_tributarios')

    clasificaciones = ClasificacionTributaria.objects.filter(id_contribuyente=contribuyente)
    
    # Esta vista ahora puede usar el nombre de la nueva URL 
    # 'cargar_clasificaciones_masivo' en su template HTML
    return render(request, 'clasificaciones_por_contribuyente.html', {
        'usuario': usuario,
        'contribuyente': contribuyente,
        'clasificaciones': clasificaciones
    })


def crear_clasificacion(request, contribuyente_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

    try:
        # Asegúrate de que el usuario tiene acceso a este contribuyente
        contribuyente = Contribuyente.objects.get(pk=contribuyente_id, id_usuario=usuario)
    except Contribuyente.DoesNotExist:
        messages.error(request, 'Contribuyente no encontrado o no autorizado.')
        return redirect('manejo_tributarios')

    if request.method == 'POST':
        tipo_de_tributo = request.POST.get('tipo_de_tributo')
        monto_raw = request.POST.get('monto') or '0'
        codigo_raw = (request.POST.get('codigo_CIIU') or '').strip()
        regimen = request.POST.get('regimen') or ''
        fecha_de_creacion = request.POST.get('fecha_de_creacion')

        if not codigo_raw.isdigit() or len(codigo_raw) not in (4, 6):
            messages.error(request, 'Código CIIU inválido. Debe ser un número de 4 o 6 dígitos (por ejemplo 1234 o 123456).')

            form_obj = type('F', (), {})()
            form_obj.tipo_de_tributo = tipo_de_tributo
            form_obj.codigo_CIIU = codigo_raw
            form_obj.regimen = regimen
            try:
                form_obj.monto = int(monto_raw)
            except:
                form_obj.monto = monto_raw

            return render(request, 'crear_clasificacion.html', {
                'usuario': usuario,
                'contribuyente': contribuyente,
                'mode': 'crear',
                'clasificacion': form_obj
            })

        try:
            monto = int(monto_raw)
            codigo_CIIU = int(codigo_raw)

            if not fecha_de_creacion:
                from datetime import date
                fecha_de_creacion = date.today()

            nueva = ClasificacionTributaria(
                id_contribuyente=contribuyente,
                id_pais=contribuyente.id_pais,
                id_usuario=usuario,
                tipo_de_tributo=tipo_de_tributo,
                monto=monto,
                codigo_CIIU=codigo_CIIU,
                regimen=regimen,
                fecha_de_creacion=fecha_de_creacion
            )
            nueva.save() # Se guarda la clasificación en la DB
            
            # ------------------------------------------------------------------
            # ✅ CAMBIO CLAVE: Publicación del evento de correo al microservicio
            # ------------------------------------------------------------------
            
            email_payload = {
                "to": usuario.mail, 
                "subject": f"Confirmación: Nueva Clasificación para {contribuyente.nombre_comercial}",
                "body": f"""
¡Hola {usuario.nombre}!

Se ha creado una nueva clasificación tributaria en tu cuenta para el contribuyente {contribuyente.nombre_comercial}.

Detalles de la Clasificación:
- Tipo de Tributo: {tipo_de_tributo}
- Monto: {monto_raw}
- Código CIIU: {codigo_raw}
- Régimen: {regimen or 'N/A'}
- País: {contribuyente.id_pais.pais_nom}

Si no reconoces esta acción, por favor contacta a soporte.
                
Atentamente,
El equipo de Nuam
""",
                "html": False # Enviado como texto plano
            }

            try:
                # Usamos publicar_evento para enviar el payload al tópico de correo
                # ASUNCIÓN: Tu .pulsar puede manejar el envío al tópico 'persistent://public/default/email'
                publicar_evento(
                    'EMAIL_NOTIFICATION', 
                    email_payload,
                    topic='persistent://public/default/email' 
                )
            except Exception as pulsar_e:
                # Un error al enviar el correo NO debe detener la creación de la clasificación.
                print(f"ERROR PULSAR (ENVÍO DE CORREO ASÍNCRONO): {pulsar_e}")

            # ------------------------------------------------------------------

            messages.success(request, 'Clasificación creada correctamente y notificación de correo enviada.')
            return redirect('clasificaciones_por_contribuyente', contribuyente_id=contribuyente.id_contribuyente)

        except ValueError:
            messages.error(request, 'Asegúrate de que los campos numéricos tengan un formato correcto.')
        except Exception as e:
            print(f'Error al intentar crear clasificación: {e}')
            messages.error(request, f'Error de clasificación')

    return render(request, 'crear_clasificacion.html', {
        'usuario': usuario,
        'contribuyente': contribuyente,
        'mode': 'crear'
    })

def validar_string_positivo(valor, nombre_campo, index):
    if valor and not re.fullmatch(PATRON_LISTA, valor):
        # Si el valor no coincide con la lista blanca, lo rechazamos explícitamente.
        raise ValueError(f"Campo '{nombre_campo}' ('{valor}') contiene caracteres no permitidos. (Fila {index + 2})")
    return valor

def cargar_clasificaciones_masivo(request, contribuyente_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')
    usuario_id = request.session['usuario_id']
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
        contribuyente = Contribuyente.objects.get(pk=contribuyente_id, id_usuario=usuario)
    except (Usuario.DoesNotExist, Contribuyente.DoesNotExist):
        messages.error(request, 'Usuario o Contribuyente no encontrado/autorizado.')
        return redirect('manejo_tributarios')
    if request.method == 'POST':
        if 'archivo_excel' not in request.FILES:
            messages.error(request, 'No se encontró el archivo para la carga masiva.')
            return redirect('clasificaciones_por_contribuyente', contribuyente_id=contribuyente_id)
        excel_file = request.FILES['archivo_excel']
        file_name = excel_file.name.lower()
        clasificaciones_a_crear = []
        errores = []
        try:
            if file_name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(excel_file, engine='openpyxl') 
            elif file_name.endswith('.csv'):
                df = pd.read_csv(excel_file)
            else:
                messages.error(request, 'Formato de archivo inválido. Sube un archivo Excel (.xlsx o .xls) o CSV.')
                return redirect('clasificaciones_por_contribuyente', contribuyente_id=contribuyente_id)
            df.columns = df.columns.str.strip() 
            df.columns = df.columns.str.replace(r'[^\w\s]', '', regex=True) 
            COLUMNAS_ESPERADAS = {
                'Tipo de Tributo': 'tipo_de_tributo',
                'Monto': 'monto',
                'Código CIIU': 'codigo_CIIU',
                'Régimen': 'regimen',
                'Fecha de Creación': 'fecha_de_creacion',
            }
            columnas_existentes = {col_excel: col_modelo for col_excel, col_modelo in COLUMNAS_ESPERADAS.items() if col_excel in df.columns}
            columnas_obligatorias = ['Tipo de Tributo', 'Monto', 'Código CIIU']
            if not all(col in df.columns for col in columnas_obligatorias):
                 messages.error(request, f'El archivo debe contener las columnas obligatorias: {", ".join(columnas_obligatorias)}.')
                 return redirect('clasificaciones_por_contribuyente', contribuyente_id=contribuyente_id)
            with transaction.atomic():
                for index, row in df.iterrows():
                    if row.isnull().all():
                        continue
                    try:
                        data = {col_modelo: row.get(col_excel) for col_excel, col_modelo in columnas_existentes.items()}
                        
                        # Recolección y Conversión de Datos
                        tipo_de_tributo = str(data.get('tipo_de_tributo') or '').strip()
                        monto_raw = str(data.get('monto') or '').strip()
                        codigo_raw = str(data.get('codigo_CIIU') or '').strip()
                        regimen = str(data.get('regimen') or '').strip()
                        fecha_de_creacion = data.get('fecha_de_creacion')

                        # Validaciones de Seguridad para Strings
                        tipo_de_tributo = validar_string_positivo(tipo_de_tributo, 'Tipo', index)
                        regimen = validar_string_positivo(regimen, 'Régimen', index)                                       
                        # Validación de Monto
                        try:
                            # float() para manejar la notación científica o decimal antes de int()
                            monto = int(float(monto_raw)) if monto_raw else 0
                        except ValueError:
                            raise ValueError(f"Monto ('{monto_raw}') inválido, debe ser un número entero. (Fila {index + 2})")
                        
                        # Validación de Código CIIU (4 o 6 dígitos)
                        if not codigo_raw.isdigit() or len(codigo_raw) not in (4, 6):
                            raise ValueError(f"Código CIIU ('{codigo_raw}') inválido. Debe ser un número de 4 o 6 dígitos. (Fila {index + 2})")
                        codigo_CIIU = int(codigo_raw)
                        
                        # Manejo de fecha
                        if pd.isna(fecha_de_creacion) or not fecha_de_creacion:
                            fecha_de_creacion = date.today()
                        elif isinstance(fecha_de_creacion, pd.Timestamp):
                            fecha_de_creacion = fecha_de_creacion.date()
                        elif isinstance(fecha_de_creacion, str):
                            try:
                                fecha_de_creacion = pd.to_datetime(fecha_de_creacion).date()
                            except Exception:
                                raise ValueError(f"Fecha de Creación ('{fecha_de_creacion}') inválida. (Fila {index + 2})")
                        nueva_clasificacion = ClasificacionTributaria(
                            id_contribuyente=contribuyente,
                            id_pais=contribuyente.id_pais,
                            id_usuario=usuario,
                            tipo_de_tributo=tipo_de_tributo,
                            monto=monto,
                            codigo_CIIU=codigo_CIIU,
                            regimen=regimen,
                            fecha_de_creacion=fecha_de_creacion
                        )
                        clasificaciones_a_crear.append(nueva_clasificacion)

                    except Exception as e:
                        errores.append(f"Error en la fila {index + 2}: {e}")
                        raise RuntimeError("Error de validación en la fila") 
                if clasificaciones_a_crear:
                    ClasificacionTributaria.objects.bulk_create(clasificaciones_a_crear)
                    publicar_evento('CARGA MASIVA CLASIFICACIONES', {
                        'contribuyente': contribuyente.nombre_comercial,
                        'tipo_de_tributo': 'Varios',
                        'usuario': usuario.mail,
                        'cantidad': len(clasificaciones_a_crear)})           
                    messages.success(request, f'Se crearon {len(clasificaciones_a_crear)} clasificaciones correctamente.')
                else:
                    messages.warning(request, 'El archivo estaba vacío o no contenía datos válidos para la carga.')
        except RuntimeError:
             error_summary = "⚠️ **Fallo de Carga Masiva:** Se revirtió la transacción debido a errores en el archivo. Errores:<ul>" + "".join(f"<li>{err}</li>" for err in errores) + "</ul>"
             messages.error(request, error_summary)
        except Exception as e:
            print(f'Error al procesar archivo de carga masiva: {type(e).__name__} - {e}')
            messages.error(request, f'Error al procesar el archivo')
            
        return redirect('clasificaciones_por_contribuyente', contribuyente_id=contribuyente_id)
    return render(request, 'carga_masiva.html', {
        'usuario': usuario,
        'contribuyente': contribuyente
    })

def editar_clasificacion(request, clasificacion_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

    try:
        clas = ClasificacionTributaria.objects.get(pk=clasificacion_id)
        if clas.id_contribuyente.id_usuario != usuario:
            messages.error(request, 'No estás autorizado para editar esta clasificación.')
            return redirect('manejo_tributarios')
    except ClasificacionTributaria.DoesNotExist:
        messages.error(request, 'Clasificación no encontrada.')
        return redirect('manejo_tributarios')

    if request.method == 'POST':
        try:
            clas.tipo_de_tributo = request.POST.get('tipo_de_tributo')
            clas.monto = int(request.POST.get('monto') or 0)
            clas.codigo_CIIU = int(request.POST.get('codigo_CIIU') or 0)
            clas.regimen = request.POST.get('regimen') or ''

            fecha = request.POST.get('fecha_de_creacion')
            if fecha:
                clas.fecha_de_creacion = fecha

            clas.save()

            publicar_evento('CLASIFICACION EDITADA', {
                'contribuyente': clas.id_contribuyente.nombre_comercial,
                'usuario': usuario.mail,
                'tipo_de_tributo': clas.tipo_de_tributo,
                'monto': clas.monto,
                'codigo_CIIU': clas.codigo_CIIU,
                'regimen': clas.regimen
            })

            messages.success(request, 'Clasificación actualizada correctamente.')
            return redirect('clasificaciones_por_contribuyente', contribuyente_id=clas.id_contribuyente.id_contribuyente)

        except Exception as e:
            print(f'Error al actualizar clasificación: {e}')
            messages.error(request, f'Error al actualizar')

    return render(request, 'crear_clasificacion.html', {
        'usuario': usuario,
        'clasificacion': clas,
        'contribuyente': clas.id_contribuyente,
        'mode': 'editar'
    })

def eliminar_clasificacion(request, clasificacion_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

    try:
        clas = ClasificacionTributaria.objects.get(pk=clasificacion_id)
        if clas.id_contribuyente.id_usuario != usuario:
            messages.error(request, 'No estás autorizado para eliminar esta clasificación.')
            return redirect('manejo_tributarios')
    except ClasificacionTributaria.DoesNotExist:
        messages.error(request, 'Clasificación no encontrada.')
        return redirect('manejo_tributarios')

    if request.method == 'POST':
        contrib_id = clas.id_contribuyente.id_contribuyente
        clas.delete()
        messages.success(request, 'Clasificación eliminada correctamente.')
        return redirect('clasificaciones_por_contribuyente', contribuyente_id=contrib_id)
    
    publicar_evento('CLASIFICACION ELIMINADA', {
        'contribuyente': clas.id_contribuyente.nombre_comercial,
        'usuario': usuario.mail,
        'tipo_de_tributo': clas.tipo_de_tributo,
        'monto': clas.monto,
        'codigo_CIIU': clas.codigo_CIIU,
        'regimen': clas.regimen
    })

    return render(request, 'crear_clasificacion.html', {
        'usuario': usuario,
        'clasificacion': clas,
        'contribuyente': clas.id_contribuyente,
        'mode': 'eliminar'
    })


# ----------------------------
# EVENTOS (MANTENIDO INTACTO DE VIEWS2.PY)
# ----------------------------

def lista_eventos(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')
    eventos = Evento.objects.order_by("-timestamp")
    return render(request, "eventos.html", {"eventos": eventos})


# ----------------------------
# DIVISAS Y FAQ
# ----------------------------

def divisas_page(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

    return render(request, 'divisas.html', {'usuario': usuario})


def faq_page(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

    return render(request, 'faq.html', {'usuario': usuario})


# ----------------------------
# APIs
# ----------------------------

def api_convert(request):
    from_cur = request.GET.get('from_currency') or request.GET.get('from')
    to_cur = request.GET.get('to_currency') or request.GET.get('to')
    amount = request.GET.get('amount', 1)

    try:
        result = convert_currency(from_cur, to_cur, amount)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    status = 400 if "error" in result else 200
    return JsonResponse(result, status=status, safe=False)


def api_currencies(request):
    base = request.GET.get('base', 'USD')

    try:
        result = list_currencies(base)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    status = 400 if "error" in result else 200
    return JsonResponse(result, status=status, safe=False)

def api_chart_data(request):
    """
    Obtiene los datos para la visualización del dashboard.
    """
    try:
        result = get_mock_chart_data()
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    status = 400 if "error" in result else 200
    return JsonResponse(result, status=status, safe=False)