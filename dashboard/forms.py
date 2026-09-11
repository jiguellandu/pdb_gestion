from django import forms
from core.models import Eglise


class EgliseForm(forms.ModelForm):

    class Meta:
        model = Eglise
        fields = [
            "nom",
            "adresse",
            "ville",
            "telephone",
            "email",
            "actif",
        ]

        labels = {
            "nom": "Nom de l'église",
            "adresse": "Adresse",
            "ville": "Ville",
            "telephone": "Téléphone",
            "email": "Adresse e-mail",
            "actif": "Église active",
        }

        widgets = {
            "nom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. Porte des Brebis",
                }
            ),
            "adresse": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Adresse de l'église",
                }
            ),
            "ville": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. Kinshasa",
                }
            ),
            "telephone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+243 ...",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "eglise@example.com",
                }
            ),
            "actif": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
from comptes.models import Utilisateur


class AdministrateurEgliseForm(forms.ModelForm):

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Mot de passe",
            }
        ),
    )

    password_confirmation = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirmer le mot de passe",
            }
        ),
    )

    class Meta:
        model = Utilisateur
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "eglise",
        ]

        labels = {
            "username": "Nom d'utilisateur",
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Adresse e-mail",
            "eglise": "Église",
        }

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex. admin_eglise",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Prénom",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "admin@example.com",
                }
            ),
            "eglise": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirmation = cleaned_data.get("password_confirmation")

        if password and confirmation and password != confirmation:
            raise forms.ValidationError(
                "Les deux mots de passe ne correspondent pas."
            )

        return cleaned_data
from core.models import KoboConfiguration, KoboFormulaire


class KoboConfigurationForm(forms.ModelForm):

    class Meta:
        model = KoboConfiguration
        fields = [
            "eglise",
            "api_token",
            "base_url",
            "actif",
        ]

        labels = {
            "eglise": "Église",
            "api_token": "Token Kobo",
            "base_url": "URL Kobo",
            "actif": "Configuration active",
        }

        widgets = {
            "eglise": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "api_token": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Token API Kobo",
                }
            ),
            "base_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://kf.kobotoolbox.org",
                }
            ),
            "actif": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class KoboFormulaireForm(forms.ModelForm):

    class Meta:
        model = KoboFormulaire
        fields = [
            "eglise",
            "nom",
            "uid",
            "actif",
        ]

        labels = {
            "eglise": "Église",
            "nom": "Type de formulaire",
            "uid": "UID Kobo",
            "actif": "Formulaire actif",
        }

        widgets = {
            "eglise": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "nom": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "uid": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "UID du formulaire Kobo",
                }
            ),
            "actif": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }