from django.db import models
from core.models import Departement, Statut, Eglise


class Inventaire(models.Model):
    TYPE_CHOICES = [
        ("mobilier", "Mobilier"), ("equipement", "Equipement"),
        ("instrument", "Instrument"), ("autre", "Autre"),
    ]
    LOCALISATION_CHOICES = [
        ("salle principale", "Salle principale"), ("bureau", "Bureau"),
        ("reserve", "Reserve"), ("exterieur", "Exterieur"),
    ]

    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    nom_article = models.CharField(max_length=150, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    localisation = models.CharField(max_length=20, choices=LOCALISATION_CHOICES)
    quantite = models.PositiveIntegerField(default=1)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        return self.nom_article or f"Article #{self.pk}"


class SuiviActivite(models.Model):
    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    departement = models.ForeignKey(Departement, on_delete=models.PROTECT)
    statut = models.ForeignKey(Statut, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    date_activite = models.DateField(null=True, blank=True)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        dept = self.departement.nom if self.departement else ""
        return f"{dept} — {self.date_activite}"


class EvaluationSuivi(models.Model):
    SATISFACTION_CHOICES = [
        ("faible", "Faible"), ("moyenne", "Moyenne"), ("elevee", "Elevee"),
    ]

    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    departement = models.ForeignKey(Departement, on_delete=models.PROTECT)
    statut = models.ForeignKey(Statut, on_delete=models.PROTECT)
    satisfaction = models.CharField(max_length=10, choices=SATISFACTION_CHOICES)
    probleme = models.BooleanField(default=False)
    commentaire = models.TextField(blank=True)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        dept = self.departement.nom if self.departement else ""
        return f"{dept} — {self.satisfaction}"


class RenseignementCulte(models.Model):
    STATUT_PREDICATEUR_CHOICES = [
        ("interne", "Interne"), ("invite", "Invite"), ("autre", "Autre"),
    ]
    TYPE_CULTE_CHOICES = [
        ("dimanche", "Dimanche"), ("semaine", "Semaine"),
        ("special", "Special"), ("veille", "Veille"),
    ]

    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    statut_predicateur = models.CharField(max_length=10, choices=STATUT_PREDICATEUR_CHOICES)
    type_culte = models.CharField(max_length=10, choices=TYPE_CULTE_CHOICES)
    nom_predicateur = models.CharField(max_length=100, blank=True)
    date_culte = models.DateField()
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.type_culte} — {self.date_culte}"


class Presence(models.Model):
    TYPE_CHOICES = [
        ("dimanche", "Culte dimanche"),
        ("semaine", "Culte semaine"),
        ("special", "Culte special"),
        ("veille", "Veillee"),
        ("activite", "Autre activite"),
    ]

    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    date_culte = models.DateField()
    type_culte = models.CharField(max_length=15, choices=TYPE_CHOICES, default="dimanche")
    nom_activite = models.CharField(max_length=150, blank=True)
    hommes = models.PositiveIntegerField(default=0)
    femmes = models.PositiveIntegerField(default=0)
    enfants = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    class Meta:
        ordering = ["-date_culte"]

    def __str__(self):
        return f"{self.date_culte} — {self.get_type_culte_display()}"

    def total(self):
        return self.hommes + self.femmes + self.enfants


class Predication(models.Model):
    TYPE_CHOICES = [
        ("dimanche", "Culte dimanche"),
        ("semaine", "Culte semaine"),
        ("special", "Culte special"),
        ("conference", "Conference"),
    ]

    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    date_predication = models.DateField()
    predicateur = models.CharField(max_length=150)
    theme = models.CharField(max_length=200)
    texte_biblique = models.CharField(max_length=150, blank=True)
    type_culte = models.CharField(max_length=15, choices=TYPE_CHOICES, default="dimanche")
    duree_minutes = models.PositiveIntegerField(null=True, blank=True)
    resume = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_predication"]

    def __str__(self):
        return f"{self.date_predication} — {self.theme}"