from django.urls import path
from . import views

app_name = "membres"

urlpatterns = [
    path("", views.liste_membres, name="liste_membres"),
    path("nouveaux/", views.liste_nouveaux_membres, name="liste_nouveaux_membres"),
]