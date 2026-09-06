from django import forms
from .models import RendezVousPasteur, EvenementCalendrier


class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVousPasteur
        fields = ["pasteur", "membre", "nom_visiteur", "date", "heure_debut",
                  "heure_fin", "motif", "lieu", "statut", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "heure_debut": forms.TimeInput(attrs={"type": "time"}),
            "heure_fin": forms.TimeInput(attrs={"type": "time"}),
        }


class EvenementForm(forms.ModelForm):
    class Meta:
        model = EvenementCalendrier
        fields = ["titre", "type", "date_debut", "heure_debut", "heure_fin",
                  "lieu", "departement", "description"]
        widgets = {
            "date_debut": forms.DateInput(attrs={"type": "date"}),
            "heure_debut": forms.TimeInput(attrs={"type": "time"}),
            "heure_fin": forms.TimeInput(attrs={"type": "time"}),
        }