from django.contrib import admin
from .models import Finance, Depense, Achat, PreuvePaiement, Budget

admin.site.register(Finance)
admin.site.register(Depense)
admin.site.register(Achat)
admin.site.register(PreuvePaiement)
admin.site.register(Budget)