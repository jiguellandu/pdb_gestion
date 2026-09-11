from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import Finance, Depense, Achat, PreuvePaiement, Budget


ROLES_AUTORISES = ("administrateur", "tresorier")


@login_required
def liste_finances(request):
    if request.user.role not in ROLES_AUTORISES:
        messages.error(request, "Tu n'as pas acces a cette page.")
        return redirect("dashboard:accueil")

    finances = (
        Finance.objects
        .filter(eglise=request.user.eglise)
        .select_related("devise")
        .order_by("-date_transaction")
    )

    return render(
        request,
        "finance/liste_finances.html",
        {"finances": finances},
    )


@login_required
def liste_depenses(request):
    if request.user.role not in ROLES_AUTORISES:
        messages.error(request, "Tu n'as pas acces a cette page.")
        return redirect("dashboard:accueil")

    depenses = (
        Depense.objects
        .filter(eglise=request.user.eglise)
        .select_related("departement", "statut", "devise")
        .order_by("-date_transaction")
    )

    return render(
        request,
        "finance/liste_depenses.html",
        {"depenses": depenses},
    )


@login_required
def liste_achats(request):
    if request.user.role not in ROLES_AUTORISES:
        messages.error(request, "Tu n'as pas acces a cette page.")
        return redirect("dashboard:accueil")

    achats = (
        Achat.objects
        .filter(eglise=request.user.eglise)
        .select_related("departement", "statut")
        .order_by("-date_demande")
    )

    return render(
        request,
        "finance/liste_achats.html",
        {"achats": achats},
    )


@login_required
def liste_preuves_paiement(request):
    if request.user.role not in ROLES_AUTORISES:
        messages.error(request, "Tu n'as pas acces a cette page.")
        return redirect("dashboard:accueil")

    preuves = (
        PreuvePaiement.objects
        .filter(eglise=request.user.eglise)
        .select_related("departement", "devise")
        .order_by("-date_creation")
    )

    return render(
        request,
        "finance/liste_preuves_paiement.html",
        {"preuves": preuves},
    )


@login_required
def liste_budgets(request):
    if request.user.role not in ROLES_AUTORISES:
        messages.error(request, "Tu n'as pas acces a cette page.")
        return redirect("dashboard:accueil")

    budgets = (
        Budget.objects
        .filter(eglise=request.user.eglise)
        .select_related("departement", "devise")
        .order_by("-annee", "departement__nom")
    )

    return render(
        request,
        "finance/liste_budgets.html",
        {"budgets": budgets},
    )