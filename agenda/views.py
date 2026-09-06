from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import RendezVousPasteur, EvenementCalendrier
from .forms import RendezVousForm, EvenementForm
from core.tracabilite import enregistrer


@login_required
def liste_rendez_vous(request):
    user = request.user
    if user.role == "administrateur":
        rendez_vous = RendezVousPasteur.objects.all().order_by("date", "heure_debut")
    elif user.role == "pasteur":
        rendez_vous = RendezVousPasteur.objects.filter(pasteur=user).order_by("date", "heure_debut")
    else:
        rendez_vous = RendezVousPasteur.objects.none()

    return render(request, "agenda/rendez_vous.html", {"rendez_vous": rendez_vous})


@login_required
def creer_rendez_vous(request):
    user = request.user
    if user.role not in ("administrateur", "pasteur"):
        messages.error(request, "Tu n'as pas le droit de creer un rendez-vous.")
        return redirect("agenda:rendez_vous")

    if request.method == "POST":
        form = RendezVousForm(request.POST)
        if user.role == "pasteur":
            form.instance.pasteur = user
        if form.is_valid():
            rdv = form.save()
            enregistrer(request.user, "creation", "RendezVousPasteur", rdv.id, "", rdv.motif)
            messages.info(request, "Rendez-vous enregistre.")
            return redirect("agenda:rendez_vous")
    else:
        form = RendezVousForm()
        if user.role == "pasteur":
            form.fields.pop("pasteur")

    return render(request, "agenda/creer_rendez_vous.html", {"form": form})


@login_required
def liste_evenements(request):
    evenements = EvenementCalendrier.objects.all().order_by("date_debut")
    return render(request, "agenda/evenements.html", {"evenements": evenements})


@login_required
def creer_evenement(request):
    if request.user.role != "administrateur":
        messages.error(request, "Seule l'administration peut creer un evenement.")
        return redirect("agenda:evenements")

    if request.method == "POST":
        form = EvenementForm(request.POST)
        if form.is_valid():
            evenement = form.save()
            enregistrer(request.user, "creation", "EvenementCalendrier", evenement.id, "", evenement.titre)
            messages.info(request, "Evenement enregistre.")
            return redirect("agenda:evenements")
    else:
        form = EvenementForm()

    return render(request, "agenda/creer_evenement.html", {"form": form})