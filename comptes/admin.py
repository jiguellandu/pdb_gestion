from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Utilisateur
from core.models import Eglise


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (
            "Informations PDB Gestion",
            {
                "fields": (
                    "role",
                    "eglise",
                )
            },
        ),
    )

    list_display = [
        "username",
        "email",
        "role",
        "eglise",
        "is_staff",
        "is_active",
    ]

    list_filter = [
        "role",
        "eglise",
        "is_staff",
        "is_active",
    ]

    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
    ]

    ordering = [
        "username",
    ]

    def get_queryset(self, request):
        """
        Un superutilisateur voit tous les utilisateurs.
        Un autre utilisateur du système ne voit que
        les utilisateurs de sa propre église.
        """
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.eglise:
            return qs.filter(eglise=request.user.eglise)

        return qs.none()

    def get_form(self, request, obj=None, **kwargs):
        """
        Pour un administrateur normal, l'église est limitée
        à son église.
        """
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            if "eglise" in form.base_fields:
                form.base_fields["eglise"].queryset = Eglise.objects.filter(
                    id=request.user.eglise_id
                )

        return form

    def save_model(self, request, obj, form, change):
        """
        Un administrateur normal ne peut pas choisir une autre
        église. L'utilisateur est automatiquement rattaché
        à l'église de l'administrateur.
        """
        if not request.user.is_superuser:
            obj.eglise = request.user.eglise

        super().save_model(request, obj, form, change)