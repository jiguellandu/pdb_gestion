from django.urls import path
from . import views

app_name = "agenda"

urlpatterns = [
    path("rendez-vous/", views.liste_rendez_vous, name="rendez_vous"),
    path("rendez-vous/nouveau/", views.creer_rendez_vous, name="creer_rendez_vous"),
    path("evenements/", views.liste_evenements, name="evenements"),
    path("evenements/nouveau/", views.creer_evenement, name="creer_evenement"),
]