from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("finances/", views.liste_finances, name="liste_finances"),
    path("depenses/", views.liste_depenses, name="liste_depenses"),
    path("achats/", views.liste_achats, name="liste_achats"),
    path("preuves-paiement/", views.liste_preuves_paiement, name="liste_preuves_paiement"),
    path("budget/", views.liste_budgets, name="liste_budgets"),
]