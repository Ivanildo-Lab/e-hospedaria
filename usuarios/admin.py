from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Adiciona o campo empresa no formulário do Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Informações SaaS', {'fields': ('empresa', 'telefone')}),
    )
    list_display = ('username', 'email', 'empresa', 'is_staff')
    list_filter = ('empresa', 'is_staff', 'is_superuser')