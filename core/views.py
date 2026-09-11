from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404

from .models import Departement
from membres.models import Membre
from finance.models import Depense, Budget
from operations.models import SuiviActivite


@login_required
def liste_departements(request):

    departements = (
        Departement.objects
        .filter(eglise=request.user.eglise)
        .order_by("nom")
    )

    return render(
        request,
        "core/liste_departements.html",
        {
            "departements": departements,
        },
    )


@login_required
def detail_departement(request, departement_id):

    departement = get_object_or_404(
        Departement,
        id=departement_id,
        eglise=request.user.eglise,
    )

    aujourdhui = date.today()

    nb_membres = Membre.objects.filter(
        departement=departement,
        eglise=request.user.eglise,
    ).count()

    activites_mois = SuiviActivite.objects.filter(
        departement=departement,
        eglise=request.user.eglise,
        date_activite__year=aujourdhui.year,
        date_activite__month=aujourdhui.month,
    )

    budget = Budget.objects.filter(
        departement=departement,
        eglise=request.user.eglise,
        annee=aujourdhui.year,
    ).first()

    depenses_totales = (
        Depense.objects
        .filter(
            departement=departement,
            eglise=request.user.eglise,
        )
        .aggregate(total=Sum("montant"))["total"]
        or 0
    )

    return render(
        request,
        "core/detail_departement.html",
        {
            "departement": departement,
            "nb_membres": nb_membres,
            "activites_mois": activites_mois,
            "budget": budget,
            "depenses_totales": depenses_totales,
        },
    )