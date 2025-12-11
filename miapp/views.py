from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate
from .models import Usuario, ClasificacionTributaria, Contribuyente, Pais
from django.contrib.auth.hashers import make_password
import re
from django.contrib import messages
from .pulsar import publicar_evento
from .models import Evento
from django.http import JsonResponse
from .services.exchange import convert_currency, list_currencies
import pandas as pd
from datetime import date 
from django.db import transaction

# ----------------------------
# LOGIN / LOGOUT
# ----------------------------

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


def logout_view(request):
    request.session.flush() 
    messages.info(request, "Has cerrado sesión correctamente.")
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
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('crear_usuario')

    return render(request, 'Index.html', {'usuario': usuario})


# ----------------------------
# USUARIOS
# ----------------------------

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

        if not mail or not nombre or not contrasena:
            messages.error(request, "Por favor completa todos los campos.")
            return redirect('crear_usuario')

        if not re.match(patron_correo, mail):
            messages.error(request, "El formato del correo no es válido. Debe ser tipo ejemplo@gmail.com")
            return redirect('crear_usuario')

        if len(contrasena) < 6:
            messages.error(request, "La contraseña debe tener al menos 6 caracteres.")
            return redirect('crear_usuario')

        if Usuario.objects.filter(mail=mail).exists():
            messages.error(request, "Ya existe una cuenta con ese correo.")
            return redirect('crear_usuario')

        if rol not in ['cliente', 'administrador']:
            messages.error(request, "El rol seleccionado no es válido.")
            return redirect('crear_usuario')

        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            mail=mail,
            contraseña=make_password(contrasena), 
            rol=rol
        )
        nuevo_usuario.save()

        publicar_evento('USUARIO CREADO', {
            'usuario_id': nuevo_usuario.id_usuario,
            'nombre': nuevo_usuario.nombre,
            'mail': nuevo_usuario.mail,
            'rol': nuevo_usuario.rol
        })

        messages.success(request, "Cuenta creada exitosamente. ¡Ahora inicia sesión!")
        return redirect('crear_usuario')

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
        mail = request.POST.get('mail')
        
        pass_new = request.POST.get('password_new')
        pass_confirm = request.POST.get('password_confirm')

        # Validar campos obligatorios
        if not nombre or not apellido or not mail:
            messages.error(request, "Nombre, Apellido y Mail son obligatorios.")
        else:
            # Actualizar datos
            usuario.nombre = nombre
            usuario.apellido = apellido
            usuario.mail = mail

            # Lógica para cambio de contraseña (solo si se escribieron datos)
            if pass_new:
                if pass_new == pass_confirm:
                    if len(pass_new) >= 6:
                        usuario.contraseña = make_password(pass_new)
                        messages.success(request, "Perfil y contraseña actualizados correctamente.")
                    else:
                        messages.error(request, "La nueva contraseña debe tener al menos 6 caracteres.")
                        return render(request, 'cuenta.html', {'usuario': usuario})
                else:
                    messages.error(request, "Las nuevas contraseñas no coinciden.")
                    return render(request, 'cuenta.html', {'usuario': usuario})
            else:
                messages.success(request, "Perfil actualizado correctamente.")
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
    # Verificar sesión
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    if request.method == 'POST':
        usuario_id = request.session['usuario_id']
        try:
            publicar_evento('ELIMINAR CUENTA', {
                'id': usuario_id
            })
            usuario = Usuario.objects.get(pk=usuario_id)
            usuario.delete()
            
            request.session.flush()
            publicar_evento('ELIMINAR USUARIO', {
            'id': usuario.id_usuario,
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'mail': usuario.mail,
            'rol': usuario.rol
        })
            messages.success(request, "Tu cuenta ha sido eliminada permanentemente.")
            return redirect('crear_usuario') 
        
        
        
        except Usuario.DoesNotExist:
            request.session.flush()
            return redirect('crear_usuario')

    # Si intentan entrar por URL directa sin usar el botón (GET), los devolvemos
    return redirect('cuenta')

def usuarios_contribuyentes(request):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']

    try:
        admin = Usuario.objects.get(pk=usuario_id)
        if admin.rol != 'administrador':
            return redirect('index')

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

        patron_correo = r'^[a-zA-Z0-9._%+-]+@gmail.com$'
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
            empleados_str = request.POST.get('empleados')
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
            messages.error(request, f'Error al crear contribuyente: {e}')
        
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
            contribuyente.tipo = request.POST.get('tipo')
            contribuyente.situación = request.POST.get('situacion')
            contribuyente.nombre_comercial = request.POST.get('nombre_comercial')
            contribuyente.actividad_economica = request.POST.get('actividad_economica')
            contribuyente.identificador_tributario = request.POST.get('identificador_tributario')

            empleados_str = request.POST.get('empleados')
            contribuyente.empleados = int(empleados_str) if empleados_str and empleados_str.isdigit() else 0

            contribuyente.save()

            messages.success(request, 'Contribuyente actualizado correctamente.')
            return redirect('manejo_tributarios')

        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')

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
            nueva.save()

            publicar_evento('CLASIFICACION CREADA', {
            'contribuyente': contribuyente.nombre_comercial,
            'usuario': usuario.mail,
            'tipo_de_tributo': tipo_de_tributo,
            'monto': monto_raw,
            'codigo_CIIU': codigo_raw,
            'regimen': regimen
        })

            messages.success(request, 'Clasificación creada correctamente.')
            return redirect('clasificaciones_por_contribuyente', contribuyente_id=contribuyente.id_contribuyente)

        except ValueError:
            messages.error(request, 'Asegúrate de que los campos numéricos tengan un formato correcto.')
        except Exception as e:
            messages.error(request, f'Error al crear clasificación: {e}')


    return render(request, 'crear_clasificacion.html', {
        'usuario': usuario,
        'contribuyente': contribuyente,
        'mode': 'crear'
    })

def cargar_clasificaciones_masivo(request, contribuyente_id):
    if 'usuario_id' not in request.session:
        return redirect('crear_usuario')

    usuario_id = request.session['usuario_id']
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
        # Se requiere que el contribuyente pertenezca al usuario para la carga
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
            # 1. Detección de tipo de archivo y lectura con Pandas
            if file_name.endswith(('.xlsx', '.xls')):
                # Leer como Excel
                df = pd.read_excel(excel_file, engine='openpyxl')
            elif file_name.endswith('.csv'):
                # Leer como CSV (asumiendo encoding UTF-8)
                df = pd.read_csv(excel_file)
            else:
                messages.error(request, 'Formato de archivo inválido. Sube un archivo Excel (.xlsx o .xls) o CSV.')
                return redirect('clasificaciones_por_contribuyente', contribuyente_id=contribuyente_id)

            # 2. LIMPIEZA DE COLUMNAS (Solución a caracteres invisibles)
            # 1. Limpia espacios al inicio/final.
            df.columns = df.columns.str.strip() 
            # 2. Reemplaza cualquier carácter invisible o especial (como el espacio de no separación) 
            #    que no sea letra, número o espacio normal.
            df.columns = df.columns.str.replace(r'[^\w\s]', '', regex=True) 
            
            # Mapeo de columnas de Excel a atributos del modelo
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

            # 3. Procesamiento fila por fila dentro de una transacción atómica
            with transaction.atomic():
                for index, row in df.iterrows():
                    # Ignorar filas completamente vacías
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
                        # Nota: Si la fecha ya es un objeto datetime.date, se mantiene.

                        # Preparar objeto para creación masiva
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
                        # Forzar el rollback si hay un error en cualquier fila
                        raise RuntimeError("Error de validación en la fila") 

                # Si no hubo RuntimeError, guardar los datos
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
             # Si hubo un error de validación interna
             error_summary = "⚠️ **Fallo de Carga Masiva:** Se revirtió la transacción debido a errores en el archivo. Errores:<ul>" + "".join(f"<li>{err}</li>" for err in errores) + "</ul>"
             messages.error(request, error_summary)
        except Exception as e:
            # Captura errores generales de lectura de archivo
            messages.error(request, f'Error al procesar el archivo: {type(e).__name__} - {e}')
            
        return redirect('clasificaciones_por_contribuyente', contribuyente_id=contribuyente_id)

    # Si es un método GET, renderizar el formulario
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
            messages.error(request, f'Error al actualizar: {e}')

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
