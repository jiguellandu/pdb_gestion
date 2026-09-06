from .models import JournalActivite


def enregistrer(utilisateur, action, modele, objet_id="", ancienne="", nouvelle=""):
    JournalActivite.objects.create(
        utilisateur=utilisateur,
        action=action,
        modele=modele,
        objet_id=str(objet_id),
        ancienne_valeur=str(ancienne),
        nouvelle_valeur=str(nouvelle),
    )