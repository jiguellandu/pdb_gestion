from django.contrib import admin

from .models import (
    Inventaire,
    SuiviActivite,
    EvaluationSuivi,
    RenseignementCulte,
    Presence,
    Predication,
)

from core.models import Eglise


class EgliseScopedAdmin(admin.ModelAdmin):
    """
    Sécurise les données des opérations par église.

    - Le superutilisateur voit toutes les églises.
    - Un utilisateur normal voit uniquement
      les données de son église.
    """

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
        """
        Empêche un utilisateur normal de rattacher
        une donnée à une autre église.
        """

        if not request.user.is_superuser:
            obj.eglise = request.user.eglise

        super().save_model(request, obj, form, change)


@admin.register(Inventaire)
class InventaireAdmin(EgliseScopedAdmin):
    list_display = [
        "eglise",
    ]

    list_filter = [
        "eglise",
    ]


@admin.register(SuiviActivite)
class SuiviActiviteAdmin(EgliseScopedAdmin):
    list_display = [
        "eglise",
    ]

    list_filter = [
        "eglise",
    ]


@admin.register(EvaluationSuivi)
class EvaluationSuiviAdmin(EgliseScopedAdmin):
    list_display = [
        "eglise",
    ]

    list_filter = [
        "eglise",
    ]


@admin.register(RenseignementCulte)
class RenseignementCulteAdmin(EgliseScopedAdmin):
    list_display = [
        "eglise",
    ]

    list_filter = [
        "eglise",
    ]


@admin.register(Presence)
class PresenceAdmin(EgliseScopedAdmin):
    list_display = [
        "eglise",
    ]

    list_filter = [
        "eglise",
    ]


@admin.register(Predication)
class PredicationAdmin(EgliseScopedAdmin):
    list_display = [
        "eglise",
    ]

    list_filter = [
        "eglise",
    ]