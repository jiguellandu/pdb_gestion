from django.db import models
from core.models import Departement


class Membre(models.Model):
    SEXE_CHOICES = [("M", "Masculin"), ("F", "Feminin")]

    nom = models.CharField(max_length=100, blank=True)
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES)
    statut_matrimonial = models.CharField(max_length=20)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True)
    temps_passe_eglise = models.CharField(max_length=50, blank=True)
    baptise = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        return self.nom or f"Membre #{self.pk}"


class NouveauMembre(models.Model):
    SEXE_CHOICES = [("M", "Masculin"), ("F", "Feminin")]

    nom = models.CharField(max_length=100, blank=True)
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES)
    statut_matrimonial = models.CharField(max_length=20)
    baptise = models.BooleanField(default=False)
    jour_visite = models.DateField(null=True, blank=True)
    experience = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        return self.nom or f"Nouveau membre #{self.pk}"