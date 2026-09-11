from contextvars import ContextVar


_utilisateur_courant = ContextVar(
    "utilisateur_courant",
    default=None,
)


def definir_utilisateur(utilisateur):
    return _utilisateur_courant.set(utilisateur)


def obtenir_utilisateur():
    return _utilisateur_courant.get()


def reinitialiser_utilisateur(token):
    _utilisateur_courant.reset(token)