# Base-a-medias
SOY MALISIMO PAL GITHUB

sudo apt update
sudo apt install mkcert libnss3-tools -y
mkcert -install

sudo apt install docker.io -y
sudo systemctl enable --now docker
docker compose version
sudo apt install docker-compose-plugin -y


mkcert localhost
python manage.py runserver_plus --cert-file localhost.pem --key-file localhost-key.pem
python manage.py runserver_plus --cert-file localhost+2.pem --key-file localhost+2-key.pem
docker compose up -d

editar 
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

    # 🔒 RESTRICCIÓN: Si no eres admin, solo puedes editar tus propios contribuyentes
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
eli
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

    # 🔒 RESTRICCIÓN: Si no eres admin, solo puedes eliminar tus propios contribuyentes
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
clasi
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

    # 🔒 RESTRICCIÓN: admin ve todo / usuario solo los suyos
    if usuario.rol != 'administrador' and contribuyente.id_usuario != usuario:
        messages.error(request, "No autorizado.")
        return redirect('manejo_tributarios')

    clasificaciones = ClasificacionTributaria.objects.filter(id_contribuyente=contribuyente)

    return render(request, 'clasificaciones_por_contribuyente.html', {
        'usuario': usuario,
        'contribuyente': contribuyente,
        'clasificaciones': clasificaciones
    })

