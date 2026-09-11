from django.contrib import admin

from .models import (
    Finance,
    Depense,
    Achat,
    PreuvePaiement,
    Budget,
)

from core.models import Eglise, Departement


class EgliseScopedAdmin(admin.ModelAdmin):
    """
    Sécurise les modèles liés à une église.

    - Le superutilisateur voit toutes les églises.
    - Un utilisateur normal ne voit que les données
      de son église.
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

            # Sécurise le champ eglise
            if "eglise" in form.base_fields:
                form.base_fields["eglise"].queryset = Eglise.objects.filter(
                    id=request.user.eglise_id
                )

            # Sécurise le champ departement
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

            # Protection supplémentaire du département
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


@admin.register(Finance)
class FinanceAdmin(EgliseScopedAdmin):
    list_display = [
        "date_transaction",
        "montant",
        "devise",
        "eglise",
    ]

    list_filter = [
        "devise",
        "eglise",
    ]

    ordering = [
        "-date_transaction",
    ]


@admin.register(Depense)
class DepenseAdmin(EgliseScopedAdmin):
    list_display = [
        "date_transaction",
        "montant",
        "devise",
        "departement",
        "statut",
        "eglise",
    ]

    list_filter = [
        "devise",
        "departement",
        "statut",
        "eglise",
    ]

    ordering = [
        "-date_transaction",
    ]


@admin.register(Achat)
class AchatAdmin(EgliseScopedAdmin):
    list_display = [
        "date_demande",
        "departement",
        "statut",
        "eglise",
    ]

    list_filter = [
        "departement",
        "statut",
        "eglise",
    ]

    ordering = [
        "-date_demande",
    ]


@admin.register(PreuvePaiement)
class PreuvePaiementAdmin(EgliseScopedAdmin):
    list_display = [
        "date_creation",
        "departement",
        "devise",
        "eglise",
    ]

    list_filter = [
        "departement",
        "devise",
        "eglise",
    ]

    ordering = [
        "-date_creation",
    ]


@admin.register(Budget)
class BudgetAdmin(EgliseScopedAdmin):
    list_display = [
        "annee",
        "departement",
        "devise",
        "eglise",
    ]

    list_filter = [
        "annee",
        "departement",
        "devise",
        "eglise",
    ]

    ordering = [
        "-annee",
    ]