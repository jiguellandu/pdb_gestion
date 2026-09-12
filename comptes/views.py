from comptes.models import Utilisateur

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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