from django import forms
from .models import Usuario # Solo importa el modelo si lo necesitas en el formulario

class UsuarioForm(forms.ModelForm):
    # Definición del campo de contraseña para el formulario (escríbelo dos veces para confirmación)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        # 🚨 CORRECCIÓN CLAVE: Usar 'password' en lugar de 'contrasena' 🚨
        fields = ['nombre', 'apellido', 'mail', 'rol', 'password', 'password_confirm'] 
        # Nota: Generalmente se excluye 'password' de 'fields' y se maneja por separado 
        # en el formulario para poder usar password y password_confirm.
    
    # Este método asegura que las contraseñas coincidan
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError(
                "Las contraseñas no coinciden."
            )
        return cleaned_data
        
    # Este método es para guardar el usuario con la contraseña hasheada
    def save(self, commit=True):
        user = super().save(commit=False)
        # 💡 Este método DEBE hashear la contraseña 💡
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user