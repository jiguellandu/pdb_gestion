from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("departements/", views.liste_departements, name="liste_departements"),
    path("departements/<int:departement_id>/", views.detail_departement, name="detail_departement"),
]