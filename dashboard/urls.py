from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.accueil, name="accueil"),

    path(
        "synchroniser/",
        views.synchroniser,
        name="synchroniser",
    ),

    path(
        "rapports/",
        views.rapports,
        name="rapports",
    ),

    path(
        "nouvelle-eglise/",
        views.nouvelle_eglise,
        name="nouvelle_eglise",
    ),

    path(
        "nouvel-administrateur/",
        views.nouvel_administrateur,
        name="nouvel_administrateur",
    ),
    path(
       "configuration-kobo/",
       views.configuration_kobo,
       name="configuration_kobo",
),
path(
    "nouvelle-configuration-kobo/",
    views.nouvelle_configuration_kobo,
    name="nouvelle_configuration_kobo",
),
]
