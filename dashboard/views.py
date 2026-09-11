import json
from datetime import date
from io import StringIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect

from finance.models import Finance, Depense, Achat, PreuvePaiement
from membres.models import Membre, NouveauMembre
from operations.models import (
    SuiviActivite,
    Inventaire,
    EvaluationSuivi,
    RenseignementCulte,
    Predication,
)
from agenda.models import RendezVousPasteur, EvenementCalendrier
from core.models import (
    JournalActivite,
    Devise,
    Eglise,
    KoboConfiguration,
    KoboFormulaire,
)

from .forms import (
    EgliseForm,
    AdministrateurEgliseForm,
    KoboConfigurationForm,
)


@login_required
def accueil(request):
    user = request.user

    if user.role == "administrateur":
        return vue_admin(request)

    elif user.role == "chef_departement":
        return vue_chef_departement(request)

    elif user.role == "pasteur":
        return vue_pasteur(request)

    elif user.role == "secretaire":
        return redirect("membres:liste_membres")

    elif user.role == "tresorier":
        return redirect("finance:liste_finances")

    return render(request, "dashboard/acces_refuse.html")


# =============================================================
# ADMINISTRATEUR
# =============================================================

@login_required
def vue_admin(request):

    eglise = request.user.eglise

    # REPARTITION HOMMES / FEMMES

    repartition_sexe = (
        Membre.objects
        .filter(eglise=eglise)
        .values("sexe")
        .annotate(total=Count("id"))
    )

    donnees_sexe = {
        "Hommes": 0,
        "Femmes": 0,
    }

    for ligne in repartition_sexe:

        if ligne["sexe"] == "M":
            donnees_sexe["Hommes"] = ligne["total"]

        elif ligne["sexe"] == "F":
            donnees_sexe["Femmes"] = ligne["total"]

    # EVOLUTION DES FINANCES

    recettes_par_mois = (
        Finance.objects
        .filter(eglise=eglise)
        .annotate(mois=TruncMonth("date_transaction"))
        .values("mois")
        .annotate(total=Sum("montant"))
        .order_by("mois")
    )

    depenses_par_mois = (
        Depense.objects
        .filter(eglise=eglise)
        .annotate(mois=TruncMonth("date_transaction"))
        .values("mois")
        .annotate(total=Sum("montant"))
        .order_by("mois")
    )

    mois_labels = sorted(
        set(
            [r["mois"] for r in recettes_par_mois]
            + [d["mois"] for d in depenses_par_mois]
        )
    )

    recettes_dict = {
        r["mois"]: float(r["total"])
        for r in recettes_par_mois
    }

    depenses_dict = {
        d["mois"]: float(d["total"])
        for d in depenses_par_mois
    }

    evolution = {
        "labels": [
            m.strftime("%b %Y")
            for m in mois_labels
            if m
        ],
        "recettes": [
            recettes_dict.get(m, 0)
            for m in mois_labels
            if m
        ],
        "depenses": [
            depenses_dict.get(m, 0)
            for m in mois_labels
            if m
        ],
    }

    # DEPENSES PAR DEPARTEMENT

    depenses_dept = (
        Depense.objects
        .filter(eglise=eglise)
        .values("departement__nom")
        .annotate(total=Sum("montant"))
        .order_by("-total")
    )

    depenses_departement = {
        "labels": [
            d["departement__nom"]
            for d in depenses_dept
        ],
        "valeurs": [
            float(d["total"])
            for d in depenses_dept
        ],
    }

    # OFFRANDES PAR DEVISE

    offrandes_par_devise = (
        Finance.objects
        .filter(
            eglise=eglise,
            type="offrande"
        )
        .values("devise__code")
        .annotate(total=Sum("montant"))
    )

   # FLUX D'ACTIVITE

    rendez_vous_aujourdhui = (
        RendezVousPasteur.objects
        .filter(
            eglise=eglise,
            date=date.today()
        )
        .order_by("heure_debut")
    )

    evenements_a_venir = (
        EvenementCalendrier.objects
        .filter(
            eglise=eglise,
            date_debut__gte=date.today()
        )
        .order_by("date_debut")[:5]
    )

    activites_recentes = (
        JournalActivite.objects
        .filter(utilisateur__eglise=eglise)
        .select_related("utilisateur")
        .order_by("-id")[:6]
    )
    # CONTEXTE ADMIN

    contexte = {
        "nb_membres": (
            Membre.objects
            .filter(eglise=eglise)
            .count()
        ),

        "nb_nouveaux_membres": (
            NouveauMembre.objects
            .filter(eglise=eglise)
            .count()
        ),

        "offrandes_par_devise": offrandes_par_devise,

        "achats_en_attente": (
            Achat.objects
            .filter(
                eglise=eglise,
                statut__nom="attente"
            )
            .count()
        ),

        "nb_inventaire": (
            Inventaire.objects
            .filter(eglise=eglise)
            .count()
        ),

        "nb_suivi_activites": (
            SuiviActivite.objects
            .filter(eglise=eglise)
            .count()
        ),

        "nb_evaluations": (
            EvaluationSuivi.objects
            .filter(eglise=eglise)
            .count()
        ),

        "nb_renseignements_culte": (
            RenseignementCulte.objects
            .filter(eglise=eglise)
            .count()
        ),

        "nb_preuves_paiement": (
            PreuvePaiement.objects
            .filter(eglise=eglise)
            .count()
        ),

        "nb_evenements": (
            EvenementCalendrier.objects
            .filter(eglise=eglise)
            .count()
        ),

        "nb_rendez_vous": (
            RendezVousPasteur.objects
            .filter(eglise=eglise)
            .count()
        ),

        "dernieres_depenses": (
            Depense.objects
            .filter(eglise=eglise)
            .select_related("departement", "statut")
            .order_by("-date_creation")[:5]
        ),

        "donnees_sexe_json": json.dumps(donnees_sexe),

        "evolution_json": json.dumps(evolution),

        "depenses_departement_json": json.dumps(
            depenses_departement
        ),

        "rendez_vous_aujourdhui": rendez_vous_aujourdhui,

        "evenements_a_venir": evenements_a_venir,

        "activites_recentes": activites_recentes,
    }

    return render(
        request,
        "dashboard/admin.html",
        contexte
    )


# =============================================================
# CHEF DE DEPARTEMENT
# =============================================================

@login_required
def vue_chef_departement(request):

    eglise = request.user.eglise

    contexte = {
        "departement": None,

        "activites": (
            SuiviActivite.objects
            .filter(eglise=eglise)
            .select_related("departement", "statut")
            .order_by("-date_activite")[:10]
        ),

        "achats": (
            Achat.objects
            .filter(eglise=eglise)
            .exclude(statut__nom="realise")
            .select_related("departement", "statut")
        ),
    }

    return render(
        request,
        "dashboard/chef_departement.html",
        contexte
    )


# =============================================================
# PASTEUR
# =============================================================

@login_required
def vue_pasteur(request):

    eglise = request.user.eglise

    contexte = {
        "nb_membres": (
            Membre.objects
            .filter(eglise=eglise)
            .count()
        ),

        "nb_departements_actifs": (
            SuiviActivite.objects
            .filter(eglise=eglise)
            .values("departement")
            .distinct()
            .count()
        ),
"depenses_par_departement": (
            Depense.objects
            .filter(eglise=eglise)
            .values("departement__nom")
            .annotate(
                total=Sum("montant"),
                nb=Count("id")
            )
            .order_by("-total")
        ),

        "mes_rendez_vous": (
            RendezVousPasteur.objects
            .filter(
                eglise=eglise,
                pasteur=request.user
            )
            .order_by("date", "heure_debut")[:5]
        ),
    }

    return render(
        request,
        "dashboard/pasteur.html",
        contexte
    )


# =============================================================
# SYNCHRONISATION KOBO
# =============================================================

@login_required
def synchroniser(request):

    if request.user.role != "administrateur":

        messages.error(
            request,
            "Seul un administrateur peut lancer la synchronisation."
        )

        return redirect("dashboard:accueil")

    if request.method == "POST":

        sortie = StringIO()

        call_command(
    "sync_kobo",
    eglise=request.user.eglise.id,
    stdout=sortie
)

        for ligne in sortie.getvalue().splitlines():

            messages.info(
                request,
                ligne
            )

    return redirect("dashboard:accueil")


# =============================================================
# RAPPORTS
# =============================================================

@login_required
def rapports(request):

    if request.user.role != "administrateur":

        messages.error(
            request,
            "Seul un administrateur peut voir les rapports."
        )

        return redirect("dashboard:accueil")

    eglise = request.user.eglise

    aujourdhui = date.today()

    # RAPPORT MEMBRES

    total_membres = (
        Membre.objects
        .filter(eglise=eglise)
        .count()
    )

    nouveaux_ce_mois = (
        NouveauMembre.objects
        .filter(
            eglise=eglise,
            date_creation__year=aujourdhui.year,
            date_creation__month=aujourdhui.month
        )
        .count()
    )

    hommes = (
        Membre.objects
        .filter(
            eglise=eglise,
            sexe="M"
        )
        .count()
    )

    femmes = (
        Membre.objects
        .filter(
            eglise=eglise,
            sexe="F"
        )
        .count()
    )

    # RAPPORT FINANCIER

    devises = Devise.objects.all()

    rapports_financiers = []

    for devise in devises:

        recettes = (
            Finance.objects
            .filter(
                eglise=eglise,
                devise=devise
            )
            .aggregate(total=Sum("montant"))["total"]
            or 0
        )

        depenses = (
            Depense.objects
            .filter(
                eglise=eglise,
                devise=devise
            )
            .aggregate(total=Sum("montant"))["total"]
            or 0
        )

        dimes = (
            Finance.objects
            .filter(
                eglise=eglise,
                devise=devise,
                type="dime"
            )
            .aggregate(total=Sum("montant"))["total"]
            or 0
        )

        offrandes = (
            Finance.objects
            .filter(
                eglise=eglise,
                devise=devise,
                type="offrande"
            )
            .aggregate(total=Sum("montant"))["total"]
            or 0
        )

        rapports_financiers.append({
            "code": devise.code,
            "recettes": recettes,
            "depenses": depenses,
            "dimes": dimes,
            "offrandes": offrandes,
        })

    # RAPPORT ACTIVITES

    total_activites = (
        SuiviActivite.objects
        .filter(eglise=eglise)
        .count()
    )

    activites_realisees = (
        SuiviActivite.objects
        .filter(
            eglise=eglise,
            statut__nom="realise"
        )
        .count()
    )

    activites_annulees = (
        SuiviActivite.objects
        .filter(
            eglise=eglise,
            statut__nom="annule"
        )
        .count()
    )

    total_predications = (
        Predication.objects
        .filter(eglise=eglise)
        .count()
    )

    # CONTEXTE FINAL

    contexte = {
        "total_membres": total_membres,

        "nouveaux_ce_mois": nouveaux_ce_mois,

        "hommes": hommes,

        "femmes": femmes,

        "rapports_financiers": rapports_financiers,

        "total_activites": total_activites,

        "activites_realisees": activites_realisees,

        "activites_annulees": activites_annulees,

        "total_predications": total_predications,
    }

    return render(
        request,
        "dashboard/rapports.html",
        contexte
    )
def est_super_admin(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(est_super_admin)
def nouvelle_eglise(request):

    if request.method == "POST":
        form = EgliseForm(request.POST)

        if form.is_valid():
            eglise = form.save()

            messages.success(
                request,
                f"L'église « {eglise.nom} » a été créée avec succès."
            )

            return redirect("dashboard:nouvelle_eglise")

    else:
        form = EgliseForm()

    return render(
        request,
        "dashboard/nouvelle_eglise.html",
        {
            "form": form,
        },
    )
@user_passes_test(est_super_admin)
def nouvel_administrateur(request):

    if request.method == "POST":
        form = AdministrateurEgliseForm(request.POST)

        if form.is_valid():
            utilisateur = form.save(commit=False)

            utilisateur.role = "administrateur"
            utilisateur.is_staff = True
            utilisateur.is_active = True

            utilisateur.set_password(form.cleaned_data["password"])

            utilisateur.save()

            messages.success(
                request,
                f"L'administrateur « {utilisateur.username} » "
                f"a été créé avec succès pour l'église "
                f"« {utilisateur.eglise.nom} »."
            )

            return redirect("dashboard:nouvel_administrateur")

    else:
        form = AdministrateurEgliseForm()

    return render(
        request,
        "dashboard/nouvel_administrateur.html",
        {
            "form": form,
        },
    )
@login_required
@user_passes_test(est_super_admin)
def configuration_kobo(request):

    configurations = KoboConfiguration.objects.select_related("eglise").order_by(
        "eglise__nom"
    )

    formulaires = KoboFormulaire.objects.select_related("eglise").order_by(
        "eglise__nom",
        "nom",
    )

    return render(
        request,
        "dashboard/configuration_kobo.html",
        {
            "configurations": configurations,
            "formulaires": formulaires,
        },
    )
@login_required
@user_passes_test(est_super_admin)
def nouvelle_configuration_kobo(request):

    if request.method == "POST":
        form = KoboConfigurationForm(request.POST)

        if form.is_valid():
            configuration = form.save()

            messages.success(
                request,
                f"La configuration Kobo de l'église "
                f"« {configuration.eglise.nom} » "
                f"a été enregistrée avec succès."
            )

            return redirect("dashboard:configuration_kobo")

    else:
        form = KoboConfigurationForm()

    return render(
        request,
        "dashboard/nouvelle_configuration_kobo.html",
        {
            "form": form,
        },
    )