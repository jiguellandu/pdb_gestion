from django.contrib import admin

from .models import (
    RendezVousPasteur,
    EvenementCalendrier,
)

from core.models import Eglise, Departement
from membres.models import Membre
from comptes.models import Utilisateur


class EgliseScopedAdmin(admin.ModelAdmin):
    """
    Sécurise les données de l'agenda par église.

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

            # Église
            if "eglise" in form.base_fields:
                form.base_fields["eglise"].queryset = Eglise.objects.filter(
                    id=request.user.eglise_id
                )

            # Pasteur
            if "pasteur" in form.base_fields:
                form.base_fields["pasteur"].queryset = Utilisateur.objects.filter(
                    eglise_id=request.user.eglise_id,
                    role="pasteur",
                )

            # Membre
            if "membre" in form.base_fields:
                form.base_fields["membre"].queryset = Membre.objects.filter(
                    eglise_id=request.user.eglise_id
                )

            # Département
            if "departement" in form.base_fields:
                form.base_fields["departement"].queryset = Departement.objects.filter(
                    eglise_id=request.user.eglise_id
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


@admin.register(RendezVousPasteur)
class RendezVousPasteurAdmin(EgliseScopedAdmin):

    list_display = [
        "date",
        "heure_debut",
        "pasteur",
        "membre",
        "nom_visiteur",
        "eglise",
    ]

    list_filter = [
        "eglise",
        "statut",
        "date",
    ]

    search_fields = [
        "nom_visiteur",
        "motif",
        "lieu",
        "notes",
        "pasteur__username",
        "pasteur__first_name",
        "pasteur__last_name",
        "membre__nom",
    ]

    ordering = [
        "-date",
        "-heure_debut",
    ]


@admin.register(EvenementCalendrier)
class EvenementCalendrierAdmin(EgliseScopedAdmin):

    list_display = [
        "titre",
        "type",
        "date_debut",
        "lieu",
        "departement",
        "eglise",
    ]

    list_filter = [
        "eglise",
        "type",
        "departement",
        "date_debut",
    ]

    search_fields = [
        "titre",
        "lieu",
        "description",
        "departement__nom",
    ]

    ordering = [
        "-date_debut",
        "heure_debut",
    ]