from .models import JournalActivite
from .context import obtenir_utilisateur


def enregistrer(
    utilisateur=None,
    action="",
    modele="",
    objet_id="",
    ancienne="",
    nouvelle="",
):
    if utilisateur is None:
        utilisateur = obtenir_utilisateur()

    JournalActivite.objects.create(
        utilisateur=utilisateur,
        action=action,
        modele=modele,
        objet_id=str(objet_id),
        ancienne_valeur=str(ancienne),
        nouvelle_valeur=str(nouvelle),
    )