from .context import definir_utilisateur, reinitialiser_utilisateur


class UtilisateurCourantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = definir_utilisateur(
            request.user if request.user.is_authenticated else None
        )

        try:
            response = self.get_response(request)
            return response
        finally:
            reinitialiser_utilisateur(token)