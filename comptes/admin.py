from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur


class UtilisateurAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Informations PDB Gestion", {"fields": ("role", "departement")}),
    )
    list_display = ["username", "email", "role", "departement", "is_staff"]


admin.site.register(Utilisateur, UtilisateurAdmin)