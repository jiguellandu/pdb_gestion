from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import RendezVousPasteur, EvenementCalendrier

admin.site.register(RendezVousPasteur)
admin.site.register(EvenementCalendrier)