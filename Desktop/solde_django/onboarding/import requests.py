import requests

TOKEN = "8995148469:AAHNG55Z9GrPq6-X1AKDUTLsgVmB91VWaL8"
response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates")
data = response.json()

for update in data.get("result", []):
    chat = update.get("message", {}).get("chat", {})
    print(chat.get("id"), chat.get("first_name"))