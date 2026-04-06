import requests
import time
import os
from threading import Thread
from flask import Flask
from bs4 import BeautifulSoup

VOICE_TOKEN = os.getenv("VOICE_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"


# 🔊 Disparo Alexa
def trigger(jogo):
    try:
        requests.get(
            "https://api-v2.voicemonkey.io/trigger",
            params={
                "token": VOICE_TOKEN,
                "device": "golpalmeiras"
            },
            timeout=5
        )
        print(f"🔊 GOL DETECTADO EM: {jogo}")
    except Exception as e:
        print("Erro Alexa:", e)


# 🔎 Fonte 1 — Google
def get_google_score():
    try:
        url = "https://www.google.com/search?q=girona+vs+villarreal"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        scores = soup.find_all("div", class_="BNeawe deIvCb AP7Wnd")

        if len(scores) >= 2:
            return int(scores[0].text), int(scores[1].text)
    except:
        pass

    return None, None


# 🔎 Fonte 2 — fallback
def get_alt_score():
    try:
        url = "https://www.google.com/search?q=girona+villarreal+placar+ao+vivo"
        headers = {"User-Agent": "Mozilla/5.0"}

        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        spans = soup.find_all("span")
        nums = [s.text for s in spans if s.text.isdigit()]

        if len(nums) >= 2:
            return int(nums[0]), int(nums[1])
    except:
        pass

    return None, None


# 🔁 Sistema inteligente
def get_score():
    gh, ga = get_google_score()

    if gh is not None:
        return gh, ga

    print("⚠️ Google falhou, usando fallback...")
    return get_alt_score()


def monitor():
    print("🚀 MONITORAMENTO INICIADO (ULTRA RÁPIDO)")

    last_total = -1

    while True:

        gh, ga = get_score()

        if gh is None:
            print("Sem dados do jogo ainda...")
            time.sleep(10)
            continue

        total = gh + ga

        if last_total == -1:
            last_total = total

        if total > last_total:
            print(f"⚽ GOL! {gh} x {ga}")
            trigger("Girona x Villarreal")
            last_total = total

        print(f"📊 Placar atual: {gh} x {ga}")

        time.sleep(5)  # ⚡ velocidade máxima


# 🔥 Thread
Thread(target=monitor).start()

# 🌐 Servidor Railway
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
