from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Membre, NouveauMembre

ROLES_AUTORISES = ("administrateur", "secretaire")


@login_required
def liste_membres(request):
    if request.user.role not in ROLES_AUTORISES:
        messages.error(request, "Tu n'as pas acces a cette page.")
        return redirect("dashboard:accueil")
    membres = Membre.objects.select_related("departement").order_by("-date_creation")
    return render(request, "membres/liste_membres.html", {"membres": membres})


@login_required
def liste_nouveaux_membres(request):
    if request.user.role not in ROLES_AUTORISES:
        messages.error(request, "Tu n'as pas acces a cette page.")
        return redirect("dashboard:accueil")
    nouveaux = NouveauMembre.objects.order_by("-date_creation")
    return render(request, "membres/liste_nouveaux_membres.html", {"nouveaux": nouveaux})