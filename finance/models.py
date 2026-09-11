from django.db import models
from django.db.models import Sum
from core.models import Departement, Devise, Statut, Eglise
from membres.models import Membre


class Finance(models.Model):
    TYPE_CHOICES = [
        ("offrande", "Offrande"), ("dime", "Dime"),
        ("don", "Don"), ("action de grace", "Action de grace"),
    ]
    MEMBRE_TYPE_CHOICES = [
        ("existant", "Membre existant"), ("nouveau membre", "Nouveau membre"),
        ("inconnu", "Inconnu"), ("eglise", "Eglise"),
    ]

    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    devise = models.ForeignKey(Devise, on_delete=models.PROTECT)
    montant = models.DecimalField(max_digits=14, decimal_places=2)
    membre_type = models.CharField(max_length=20, choices=MEMBRE_TYPE_CHOICES)
    membre = models.ForeignKey(Membre, on_delete=models.SET_NULL, null=True, blank=True)
    date_transaction = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        devise_code = self.devise.code if self.devise else ""
        return f"{self.type} — {self.montant} {devise_code} ({self.date_transaction})"


class Depense(models.Model):
    MODE_PAIEMENT_CHOICES = [
        ("especes", "Especes"), ("mobile money", "Mobile money"), ("banque", "Banque"),
    ]

    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    type_depense = models.CharField(max_length=100)
    devise = models.ForeignKey(Devise, on_delete=models.PROTECT)
    montant = models.DecimalField(max_digits=14, decimal_places=2)
    mode_paiement = models.CharField(max_length=30, choices=MODE_PAIEMENT_CHOICES)
    statut = models.ForeignKey(Statut, on_delete=models.PROTECT)
    departement = models.ForeignKey(Departement, on_delete=models.PROTECT)
    date_transaction = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        devise_code = self.devise.code if self.devise else ""
        return f"{self.type_depense} — {self.montant} {devise_code}"


class PreuvePaiement(models.Model):
    MODE_PAIEMENT_CHOICES = [
        ("especes", "Especes"), ("mobile money", "Mobile money"), ("banque", "Banque"),
    ]

    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    depense = models.ForeignKey(Depense, on_delete=models.SET_NULL, null=True, blank=True)
    departement = models.ForeignKey(Departement, on_delete=models.PROTECT)
    devise = models.ForeignKey(Devise, on_delete=models.PROTECT)
    montant = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    mode_paiement = models.CharField(max_length=30, choices=MODE_PAIEMENT_CHOICES)
    fichier = models.FileField(upload_to="preuves_paiement/", null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        devise_code = self.devise.code if self.devise else ""
        dept = self.departement.nom if self.departement else ""
        return f"Preuve — {self.montant} {devise_code} ({dept})"


class Achat(models.Model):
    URGENCE_CHOICES = [
        ("faible", "Faible"), ("moyenne", "Moyenne"), ("urgente", "Urgente"),
    ]

    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    departement = models.ForeignKey(Departement, on_delete=models.PROTECT)
    statut = models.ForeignKey(Statut, on_delete=models.PROTECT)
    urgence = models.CharField(max_length=10, choices=URGENCE_CHOICES)
    description = models.TextField(blank=True)
    date_demande = models.DateField(auto_now_add=True)
    kobo_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)
    def __str__(self):
        dept = self.departement.nom if self.departement else ""
        return f"{self.description or 'Achat'} — {dept}"


class Budget(models.Model):
    eglise = models.ForeignKey(Eglise, on_delete=models.CASCADE, null=True, blank=True)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)
    annee = models.PositiveIntegerField()
    montant_prevu = models.DecimalField(max_digits=14, decimal_places=2)
    devise = models.ForeignKey(Devise, on_delete=models.PROTECT)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("departement", "annee", "devise")

    def __str__(self):
        return f"{self.departement.nom} — {self.annee}"

    def montant_depense(self):
        total = Depense.objects.filter(
            departement=self.departement,
            date_transaction__year=self.annee,
            devise=self.devise,
        ).aggregate(total=Sum("montant"))["total"]
        return total or 0

    def montant_disponible(self):
        return self.montant_prevu - self.montant_depense()

    def pourcentage_utilise(self):
        if self.montant_prevu == 0:
            return 0
        return round((self.montant_depense() / self.montant_prevu) * 100, 1)