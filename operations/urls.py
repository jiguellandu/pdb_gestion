from django.urls import path
from . import views

app_name = "operations"

urlpatterns = [
    path("inventaire/", views.liste_inventaire, name="liste_inventaire"),
    path("suivi-activites/", views.liste_suivi_activites, name="liste_suivi_activites"),
    path("evaluations/", views.liste_evaluations, name="liste_evaluations"),
    path("renseignements-culte/", views.liste_renseignements_culte, name="liste_renseignements_culte"),
    path("presences/", views.liste_presences, name="liste_presences"),
    path("presences/nouvelle/", views.creer_presence, name="creer_presence"),
    path("predications/", views.liste_predications, name="liste_predications"),
    path("predications/nouvelle/", views.creer_predication, name="creer_predication"),
]