from django.contrib import admin

from .models import (
    Eglise,
    Departement,
    Devise,
    Statut,
    PermissionFormulaire,
    JournalActivite,
)


@admin.register(Eglise)
class EgliseAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "ville",
        "telephone",
        "email",
        "actif",
        "date_creation",
    ]
    list_filter = ["actif", "ville"]
    search_fields = ["nom", "ville", "telephone", "email"]
    ordering = ["nom"]

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "eglise",
        "responsable",
        "adjoint",
        "telephone",
        "date_creation",
    ]
    list_filter = ["eglise"]
    search_fields = [
        "nom",
        "responsable",
        "adjoint",
        "telephone",
    ]
    ordering = ["eglise", "nom"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.eglise_id:
            return qs.filter(eglise_id=request.user.eglise_id)

        return qs.none()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            if "eglise" in form.base_fields:
                form.base_fields["eglise"].queryset = Eglise.objects.filter(
                    id=request.user.eglise_id
                )

        return form

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.eglise = request.user.eglise

        super().save_model(request, obj, form, change)


@admin.register(Devise)
class DeviseAdmin(admin.ModelAdmin):
    list_display = ["code"]
    search_fields = ["code"]
    ordering = ["code"]


@admin.register(Statut)
class StatutAdmin(admin.ModelAdmin):
    list_display = ["nom"]
    search_fields = ["nom"]
    ordering = ["nom"]


@admin.register(PermissionFormulaire)
class PermissionFormulaireAdmin(admin.ModelAdmin):
    list_display = [
        "formulaire",
        "departement",
        "role_autorise",
    ]
    list_filter = [
        "formulaire",
        "departement",
        "role_autorise",
    ]
    search_fields = [
        "formulaire",
        "role_autorise",
        "departement__nom",
    ]
    ordering = [
        "formulaire",
        "departement",
        "role_autorise",
    ]


@admin.register(JournalActivite)
class JournalActiviteAdmin(admin.ModelAdmin):
    list_display = [
        "date_action",
        "utilisateur",
        "action",
        "modele",
        "objet_id",
    ]
    list_filter = ["action", "modele"]
    readonly_fields = [
        f.name for f in JournalActivite._meta.fields
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False