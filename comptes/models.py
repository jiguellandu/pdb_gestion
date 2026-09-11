from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import Eglise


class Utilisateur(AbstractUser):

    ROLE_CHOICES = [
        ("super_admin", "Super administrateur"),
        ("administrateur", "Administrateur"),
        ("chef_departement", "Chef de departement"),
        ("pasteur", "Pasteur"),
        ("secretaire", "Secretaire"),
        ("tresorier", "Tresorier"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    eglise = models.ForeignKey(
        Eglise,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )