from django.db import models
from django.conf import settings


class Departement(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    responsable = models.CharField(max_length=150, blank=True)
    adjoint = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    date_creation = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nom


class Devise(models.Model):
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code


class Statut(models.Model):
    nom = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nom


class PermissionFormulaire(models.Model):
    formulaire = models.CharField(max_length=50)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, null=True, blank=True)
    role_autorise = models.CharField(max_length=30)

    class Meta:
        unique_together = ("formulaire", "departement", "role_autorise")


class JournalActivite(models.Model):
    ACTION_CHOICES = [
        ("creation", "Creation"),
        ("modification", "Modification"),
        ("suppression", "Suppression"),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=15, choices=ACTION_CHOICES)
    modele = models.CharField(max_length=100)
    objet_id = models.CharField(max_length=50, blank=True)
    ancienne_valeur = models.TextField(blank=True)
    nouvelle_valeur = models.TextField(blank=True)
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_action"]

    def str(self):
        return f"{self.date_action} — {self.utilisateur} — {self.action} — {self.modele}"

