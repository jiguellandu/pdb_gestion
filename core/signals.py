from django.db.models.signals import post_save
from django.dispatch import receiver
from membres.models import Membre
from finance.models import Finance, Depense, Achat
from .tracabilite import enregistrer


@receiver(post_save, sender=Membre)
def tracer_membre(sender, instance, created, **kwargs):
    action = "creation" if created else "modification"
    enregistrer(None, action, "Membre", instance.id, "", instance.nom)


@receiver(post_save, sender=Finance)
def tracer_finance(sender, instance, created, **kwargs):
    action = "creation" if created else "modification"
    enregistrer(None, action, "Finance", instance.id, "", f"{instance.montant} {instance.type}")


@receiver(post_save, sender=Depense)
def tracer_depense(sender, instance, created, **kwargs):
    action = "creation" if created else "modification"
    enregistrer(None, action, "Depense", instance.id, "", f"{instance.montant} {instance.type_depense}")


@receiver(post_save, sender=Achat)
def tracer_achat(sender, instance, created, **kwargs):
    action = "creation" if created else "modification"
    enregistrer(None, action, "Achat", instance.id, "", instance.description)