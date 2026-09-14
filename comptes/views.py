from comptes.models import Utilisateur

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connection


def connexion(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        print("DIAGNOSTIC LOGIN - username :", repr(username))
        print(
            "DIAGNOSTIC LOGIN - longueur mot de passe :",
            len(password) if password else 0
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        print("DIAGNOSTIC DB - NAME :", connection.settings_dict.get("NAME"))
        print("DIAGNOSTIC DB - HOST :", connection.settings_dict.get("HOST"))
        print(
            "DIAGNOSTIC DB - nombre utilisateurs :",
            Utilisateur.objects.count()
        )
        print(
            "DIAGNOSTIC DB - recherche jiguel :",
            list(
                Utilisateur.objects.filter(username="jiguel").values(
                    "username",
                    "eglise_id",
                    "is_superuser",
                    "is_staff"
                )
            )
        )

        u_test = Utilisateur.objects.filter(username=username).first()

        print(
            "DIAGNOSTIC LOGIN - check_password :",
            u_test.check_password(password) if u_test else "UTILISATEUR ABSENT"
        )

        print("DIAGNOSTIC LOGIN - utilisateur :", user)

        if user is not None:
            login(request, user)
            return redirect("dashboard:accueil")

        return render(
            request,
            "comptes/connexion.html",
            {"erreur": "Identifiants incorrects"},
        )

    return render(request, "comptes/connexion.html")
def deconnexion(request):
    logout(request)
    return redirect("comptes:connexion")