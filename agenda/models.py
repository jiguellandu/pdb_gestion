from django.db import models
from django.conf import settings

from core.models import Eglise, Departement
from membres.models import Membre


class RendezVousPasteur(models.Model):
    eglise = models.ForeignKey(
        Eglise,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rendez_vous_pasteurs",
    )

    STATUT_CHOICES = [
        ("prevu", "Prevu"),
        ("confirme", "Confirme"),
        ("termine", "Termine"),
        ("annule", "Annule"),
    ]

    pasteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rendez_vous",
        limit_choices_to={"role": "pasteur"},
    )

    membre = models.ForeignKey(
        Membre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    nom_visiteur = models.CharField(max_length=150, blank=True)
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField(null=True, blank=True)
    motif = models.CharField(max_length=200, blank=True)
    lieu = models.CharField(max_length=150, blank=True)
    statut = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        default="prevu",
    )
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} {self.heure_debut} — {self.pasteur}"


class EvenementCalendrier(models.Model):
    eglise = models.ForeignKey(
        Eglise,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="evenements_calendrier",
    )

    TYPE_CHOICES = [
        ("culte", "Culte"),
        ("reunion", "Reunion"),
        ("formation", "Formation"),
        ("conference", "Conference"),
        ("mariage", "Mariage"),
        ("autre", "Autre"),
    ]

    titre = models.CharField(max_length=200)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    date_debut = models.DateField()
    heure_debut = models.TimeField(null=True, blank=True)
    heure_fin = models.TimeField(null=True, blank=True)
    lieu = models.CharField(max_length=150, blank=True)

    departement = models.ForeignKey(
        Departement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} ({self.date_debut})"