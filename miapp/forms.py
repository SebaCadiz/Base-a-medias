from django import forms
from .models import Usuario, CalificacionTributaria

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['id_usuario','Usu_nombre','Usu_contraseña','Usu_email', 'Usu_telefono']

class CalificacionTributariaForm(forms.ModelForm):
    class Meta:
        model = CalificacionTributaria
        # Estos son los campos de tu NUEVO modelo
        fields = ['nombre', 'descripcion', 'tasa_o_factor', 'pais']
        
        # (Opcional) Añade widgets para que se vea mejor
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tasa_o_factor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pais': forms.Select(attrs={'class': 'form-select'}),
        }