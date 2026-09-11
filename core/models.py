from django.db import models
from django.conf import settings


class Eglise(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    adresse = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


class KoboConfiguration(models.Model):
    eglise = models.OneToOneField(
        Eglise,
        on_delete=models.CASCADE,
        related_name="kobo_configuration",
    )

    api_token = models.TextField()

    base_url = models.URLField(
        default="https://kf.kobotoolbox.org"
    )

    actif = models.BooleanField(default=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Kobo - {self.eglise.nom}"


class KoboFormulaire(models.Model):

    FORMULAIRE_CHOICES = [
        ("achats", "Achats"),
        ("finances", "Finances"),
        ("depenses", "Dépenses"),
        ("membres", "Membres"),
        ("nouveaux_membres", "Nouveaux membres"),
        ("inventaire", "Inventaire"),
        ("suivi_activites", "Suivi des activités"),
        ("evaluations_suivi", "Évaluations du suivi"),
        ("renseignements_culte", "Renseignements du culte"),
        ("preuves_paiement", "Preuves de paiement"),
    ]

    eglise = models.ForeignKey(
        Eglise,
        on_delete=models.CASCADE,
        related_name="kobo_formulaires",
    )

    nom = models.CharField(
        max_length=50,
        choices=FORMULAIRE_CHOICES,
    )

    uid = models.CharField(max_length=100)

    actif = models.BooleanField(default=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["eglise", "nom"],
                name="unique_kobo_formulaire_eglise_nom",
            ),
            models.UniqueConstraint(
                fields=["eglise", "uid"],
                name="unique_kobo_formulaire_eglise_uid",
            ),
        ]

    def __str__(self):
        return f"{self.eglise.nom} - {self.get_nom_display()}"


class Departement(models.Model):
    eglise = models.ForeignKey(
        Eglise,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    nom = models.CharField(max_length=50)
    responsable = models.CharField(max_length=150, blank=True)
    adjoint = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    date_creation = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("eglise", "nom")

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
    departement = models.ForeignKey(
        Departement,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
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
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    action = models.CharField(
        max_length=15,
        choices=ACTION_CHOICES,
    )

    modele = models.CharField(max_length=100)
    objet_id = models.CharField(max_length=50, blank=True)
    ancienne_valeur = models.TextField(blank=True)
    nouvelle_valeur = models.TextField(blank=True)
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_action"]

    def __str__(self):
        return (
            f"{self.date_action} — "
            f"{self.utilisateur} — "
            f"{self.action} — "
            f"{self.modele}"
        )