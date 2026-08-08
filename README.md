# Solde — projet Django

Parcours en 3 étapes :

1. **`/`** — formulaire d'inscription (5 champs : prénom, nom, e-mail, téléphone, mot de passe).
2. **`/verification/`** — formulaire à 1 champ (code de vérification).
3. **`/etape-1/` à `/etape-4/`** — 4 pages présentant les étapes suivantes du parcours.

Chaque formulaire est validé côté serveur avec Django Forms : si un champ est invalide, la page se réaffiche avec un message d'erreur sous le champ concerné ; sinon on est redirigé vers la page suivante.

## Installation

```bash
python -m venv venv
source venv/bin/activate      # sous Windows : venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Puis ouvrir http://127.0.0.1:8000/

## Structure

```
solde_django/
├── manage.py
├── requirements.txt
├── solde_django/        # config du projet (settings, urls, wsgi, asgi)
└── onboarding/           # app contenant les vues, formulaires et templates
    ├── forms.py          # InscriptionForm (5 champs) et VerificationForm (1 champ)
    ├── views.py
    ├── urls.py
    ├── templates/onboarding/
    │   ├── base.html
    │   ├── inscription.html
    │   ├── verification.html
    │   └── etape-1.html … etape-4.html
    └── static/onboarding/style.css
```

## Personnaliser

- Les champs du formulaire d'inscription se modifient dans `onboarding/forms.py`.
- Le contenu de chaque étape se modifie directement dans les templates `etape-1.html` à `etape-4.html`.
- Les couleurs et polices sont centralisées dans `onboarding/static/onboarding/style.css` (variables CSS en haut du fichier).
