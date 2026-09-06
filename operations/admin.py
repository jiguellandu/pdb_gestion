from django.contrib import admin
from .models import Inventaire, SuiviActivite, EvaluationSuivi, RenseignementCulte, Presence, Predication

admin.site.register(Inventaire)
admin.site.register(SuiviActivite)
admin.site.register(EvaluationSuivi)
admin.site.register(RenseignementCulte)
admin.site.register(Presence)
admin.site.register(Predication)