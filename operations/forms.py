from django import forms
from .models import Presence, Predication


class PresenceForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = ["date_culte", "type_culte", "nom_activite", "hommes", "femmes", "enfants"]
        widgets = {
            "date_culte": forms.DateInput(attrs={"type": "date"}),
        }
class PredicationForm(forms.ModelForm):
    class Meta:
        model = Predication
        fields = ["date_predication", "predicateur", "theme", "texte_biblique", "type_culte", "duree_minutes", "resume"]
        widgets = {
            "date_predication": forms.DateInput(attrs={"type": "date"}),
            "resume": forms.Textarea(attrs={"rows": 4}),
        }