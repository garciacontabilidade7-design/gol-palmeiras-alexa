import requests
from bs4 import BeautifulSoup
import time
import os

VOICE_TOKEN = os.environ.get("VOICE_TOKEN")
VOICE_DEVICE = os.environ.get("VOICE_DEVICE")

# URL mobile do jogo (ESSA FUNCIONA COM SCRAPING)
URL = "https://m.flashscore.com.br/jogo/futebol/italia/serie-a/lecce-atalanta/"

def pegar_placar():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        score = soup.find("div", class_="score")
        if score:
            placar = score.text.strip().split(":")
            return (int(placar[0]), int(placar[1]))
        return None

    except Exception as e:
        print("Erro:", e)
        return None

def enviar_alerta():
    url = f"https://api.voicemonkey.io/trigger?AccessToken={VOICE_TOKEN}&Device={VOICE_DEVICE}&MonkeyType=smart&CustomMessage=Gol!"
    try:
        requests.get(url)
        print("🔔 GOL DETECTADO!")
    except:
        print("Erro ao enviar alerta")

ultimo = None

print("🚀 Monitorando jogo (Flashscore)...")

while True:
    placar = pegar_placar()

    if placar:
        print(f"Placar: {placar[0]} x {placar[1]}")

        if ultimo is None:
            ultimo = placar

        if placar != ultimo:
            enviar_alerta()
            ultimo = placar

    else:
        print("Sem placar ainda...")

    time.sleep(20)
