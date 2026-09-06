from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import Departement


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ("administrateur", "Administrateur"),
        ("chef_departement", "Chef de departement"),
        ("pasteur", "Pasteur"),
        ("secretaire", "Secretaire"),
        ("tresorier", "Tresorier"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)