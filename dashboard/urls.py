from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("synchroniser/", views.synchroniser, name="synchroniser"),
    path("rapports/", views.rapports, name="rapports"),
]