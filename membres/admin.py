from django.contrib import admin

from .models import Membre, NouveauMembre
from core.models import Eglise, Departement


class EgliseScopedAdmin(admin.ModelAdmin):
    """
    Sécurise les données des membres par église.

    Le superutilisateur voit toutes les églises.
    Un utilisateur normal voit uniquement
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

            # Le champ église ne doit proposer que
            # l'église de l'utilisateur.
            if "eglise" in form.base_fields:
                form.base_fields["eglise"].queryset = Eglise.objects.filter(
                    id=request.user.eglise_id
                )

            # Le département ne doit proposer que
            # les départements de son église.
            if "departement" in form.base_fields:
                form.base_fields["departement"].queryset = Departement.objects.filter(
                    eglise_id=request.user.eglise_id
                )

        return form

    def save_model(self, request, obj, form, change):
        """
        Empêche un utilisateur normal de rattacher
        un membre à une autre église.

        Vérifie également que le département
        appartient bien à son église.
        """

        if not request.user.is_superuser:
            obj.eglise = request.user.eglise

            if hasattr(obj, "departement_id") and obj.departement_id:
                departement = Departement.objects.filter(
                    id=obj.departement_id,
                    eglise_id=request.user.eglise_id
                ).first()

                if departement is None:
                    raise PermissionError(
                        "Ce département n'appartient pas à votre église."
                    )

        super().save_model(request, obj, form, change)


@admin.register(Membre)
class MembreAdmin(EgliseScopedAdmin):
    list_display = [
        "nom",
        "eglise",
        "departement",
    ]

    list_filter = [
        "eglise",
        "departement",
    ]

    search_fields = [
        "nom",
    ]

    ordering = [
        "nom",
    ]


@admin.register(NouveauMembre)
class NouveauMembreAdmin(EgliseScopedAdmin):
    list_display = [
        "nom",
        "eglise",
    ]

    list_filter = [
        "eglise",
    ]

    search_fields = [
        "nom",
    ]

    ordering = [
        "nom",
    ]