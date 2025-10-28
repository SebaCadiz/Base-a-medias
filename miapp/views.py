from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import CalificacionTributaria
from .forms import CalificacionTributariaForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages


# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

def CrearUsuario(request):
    if request.method == 'POST':
        id_usuario = request.POST.get('id_usuario')
        usu_nombre = request.POST.get('usu_nombre')
        usu_email = request.POST.get('usu_email')
        usu_telefono = request.POST.get('usu_telefono') 
        usu_contraseña = request.POST.get('usu_contraseña')

        if User.objects.filter(username=id_usuario).exists():
            messages.error(request, 'El ID de usuario (RUT) ya está registrado.')
            return redirect('login') 
        try:
            user = User.objects.create_user(
                username=id_usuario,    
                password=usu_contraseña,
                email=usu_email,
                first_name=usu_nombre   
            )
            login(request, user)
            return redirect('index')

        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {e}')
            return redirect('login')
    return redirect('login')

# Ver la tabla

@login_required
def lista_de_calificaciones(request):
    items = CalificacionTributaria.objects.all()
    contexto = {
        'lista_de_items': items
    }
    return render(request, 'Clasificacion_tributaria.html', contexto)


# 2. CREATE (Crear)
@login_required
def clasificacion_crear(request):
    if request.method == 'POST':
        form = CalificacionTributariaForm(request.POST)
        if form.is_valid():
            form.save() # Guarda el nuevo item en la BD
            return redirect('clasificacion_lista') # Redirige a la lista
    else:
        form = CalificacionTributariaForm() # Crea un formulario vacío
    
    contexto = {
        'form': form
    }
    # Renderiza la plantilla del formulario
    return render(request, 'clasificaciones_crear.html', contexto)


# 3. UPDATE (Editar)
@login_required
def clasificacion_editar(request, pk):
    # Busca el item específico por su ID (pk)
    item = get_object_or_404(CalificacionTributaria, pk=pk) 
    
    if request.method == 'POST':
        form = CalificacionTributariaForm(request.POST, instance=item)
        if form.is_valid():
            form.save() # Guarda los cambios en el item existente
            return redirect('clasificacion_lista')
    else:
        # Crea un formulario pre-llenado con los datos del item
        form = CalificacionTributariaForm(instance=item)
    
    contexto = {
        'form': form
    }
    # Reutiliza la misma plantilla del formulario de creación
    return render(request, 'clasificaciones_crear.html', contexto)


# 4. DELETE (Eliminar)
@login_required
def clasificacion_eliminar(request, pk):
    item = get_object_or_404(CalificacionTributaria, pk=pk)
    
    if request.method == 'POST':
        item.delete() # Borra el item de la BD
        return redirect('clasificacion_lista')
        
    contexto = {
        'item': item
    }
    # Muestra una página de confirmación
    return render(request, 'clasificacion_confirmar_eliminar.html', contexto)