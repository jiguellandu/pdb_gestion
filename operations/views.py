from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import (
    Inventaire,
    SuiviActivite,
    EvaluationSuivi,
    RenseignementCulte,
    Presence,
    Predication,
)
from .forms import PresenceForm, PredicationForm


@login_required
def liste_inventaire(request):
    articles = (
        Inventaire.objects
        .filter(eglise=request.user.eglise)
        .order_by("nom_article")
    )

    return render(
        request,
        "operations/liste_inventaire.html",
        {"articles": articles},
    )


@login_required
def liste_suivi_activites(request):
    activites = (
        SuiviActivite.objects
        .filter(eglise=request.user.eglise)
        .select_related("departement", "statut")
        .order_by("-date_activite")
    )

    return render(
        request,
        "operations/liste_suivi_activites.html",
        {"activites": activites},
    )


@login_required
def liste_evaluations(request):
    evaluations = (
        EvaluationSuivi.objects
        .filter(eglise=request.user.eglise)
        .select_related("departement", "statut")
        .all()
    )

    return render(
        request,
        "operations/liste_evaluations.html",
        {"evaluations": evaluations},
    )


@login_required
def liste_renseignements_culte(request):
    cultes = (
        RenseignementCulte.objects
        .filter(eglise=request.user.eglise)
        .order_by("-date_culte")
    )

    return render(
        request,
        "operations/liste_renseignements_culte.html",
        {"cultes": cultes},
    )


@login_required
def liste_presences(request):
    presences = (
        Presence.objects
        .filter(eglise=request.user.eglise)
    )

    moyenne = 0

    if presences.exists():
        totaux = [p.total() for p in presences]
        moyenne = round(sum(totaux) / len(totaux))

    return render(
        request,
        "operations/liste_presences.html",
        {
            "presences": presences,
            "moyenne": moyenne,
        },
    )


@login_required
def creer_presence(request):
    if request.user.role not in ("administrateur", "secretaire"):
        messages.error(
            request,
            "Tu n'as pas le droit d'enregistrer une presence.",
        )
        return redirect("operations:liste_presences")

    if request.method == "POST":
        form = PresenceForm(request.POST)

        if form.is_valid():
            presence = form.save(commit=False)
            presence.eglise = request.user.eglise
            presence.save()

            messages.info(request, "Presence enregistree.")
            return redirect("operations:liste_presences")
    else:
        form = PresenceForm()

    return render(
        request,
        "operations/creer_presence.html",
        {"form": form},
    )


@login_required
def liste_predications(request):
    predications = (
        Predication.objects
        .filter(eglise=request.user.eglise)
        .order_by("-date_predication")
    )

    return render(
        request,
        "operations/liste_predications.html",
        {"predications": predications},
    )


@login_required
def creer_predication(request):
    if request.user.role != "administrateur":
        messages.error(
            request,
            "Seule l'administration peut enregistrer une predication.",
        )
        return redirect("operations:liste_predications")

    if request.method == "POST":
        form = PredicationForm(request.POST)

        if form.is_valid():
            predication = form.save(commit=False)
            predication.eglise = request.user.eglise
            predication.save()

            messages.info(request, "Predication enregistree.")
            return redirect("operations:liste_predications")
    else:
        form = PredicationForm()

    return render(
        request,
        "operations/creer_predication.html",
        {"form": form},
    )