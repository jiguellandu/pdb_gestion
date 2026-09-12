from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def connexion(request):
    if request.method == "POST":
        username = request.POST.get("username")
password = request.POST.get("password")

print("DIAGNOSTIC LOGIN - username :", repr(username))
print("DIAGNOSTIC LOGIN - longueur mot de passe :", len(password) if password else 0)

user = authenticate(request, username=username, password=password)

print("DIAGNOSTIC LOGIN - utilisateur :", user)
        if user is not None:
            login(request, user)
            return redirect("dashboard:accueil")
        return render(request, "comptes/connexion.html", {"erreur": "Identifiants incorrects"})
    return render(request, "comptes/connexion.html")


@login_required
def deconnexion(request):
    logout(request)
    return redirect("comptes:connexion")