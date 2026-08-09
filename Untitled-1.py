import django, os, requests, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solde_django.settings')
django.setup()

TOKEN = '8995148469:AAHNG55Z9GrPq6-X1AKDUTLsgVmB91VWaL8'
CHAT_ID = '8849728706'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'
SERVEUR  = 'http://127.0.0.1:8000'

res = requests.get(f'{SERVEUR}/visiteurs/json/', timeout=5).json()
print('Visiteurs:', res)

visiteurs = res.get('visiteurs', [])
if not visiteurs:
    texte = '😴 Aucun visiteur actif'
else:
    lignes = [f"{len(visiteurs)} visiteur(s) en ligne"]
    for v in visiteurs:
        ip     = v['ip']
        page   = v['page']
        il_y_a = v['il_y_a']
        lignes.append(f"{ip} sur {page} depuis {il_y_a}s")
    texte = '\n'.join(lignes)

print('Texte:', texte)
r = requests.post(f'{BASE_URL}/sendMessage', json={'chat_id': CHAT_ID, 'text': texte})
print('Envoi:', r.json())
