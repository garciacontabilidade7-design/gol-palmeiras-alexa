import requests
import time
import os
from datetime import datetime, timedelta, UTC
from threading import Thread
from flask import Flask

API_KEY = os.getenv("API_KEY")
VOICE_TOKEN = os.getenv("VOICE_TOKEN")

TEAM_ID = 121  # Palmeiras

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor ativo 🚀"


def get_today_matches():
    now = datetime.now(UTC) - timedelta(hours=3)
    today = now.strftime('%Y-%m-%d')

    url = f"https://v3.football.api-sports.io/fixtures?date={today}"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        matches = []
        for m in data.get("response", []):
            if TEAM_ID in [m["teams"]["home"]["id"], m["teams"]["away"]["id"]]:
                matches.append(m)

        return matches

    except Exception as e:
        print("Erro ao buscar jogos:", e)
        return []


def get_live_match():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        for m in data.get("response", []):
            if TEAM_ID in [m["teams"]["home"]["id"], m["teams"]["away"]["id"]]:
                return m

    except Exception as e:
        print("Erro live:", e)

    return None


def trigger():
    if not VOICE_TOKEN:
        print("VOICE_TOKEN não configurado")
        return

    requests.get(
        "https://api.voicemonkey.io/trigger",
        params={
            "access_token": VOICE_TOKEN,
            "monkey": "gol_palmeiras"
        }
    )
    print("Disparou Alexa!")


def monitor():
    print("Sistema inteligente iniciado...")

    last_goals = -1

    while True:
        matches = get_today_matches()

        if not matches:
            print("Hoje NÃO tem jogo do Palmeiras. Dormindo 6h...")
            time.sleep(21600)
            continue

        print("Tem jogo hoje! Monitorando...")

        while True:
            match = get_live_match()

            if match:
                home_id = match["teams"]["home"]["id"]
                away_id = match["teams"]["away"]["id"]

                gh = match["goals"]["home"]
                ga = match["goals"]["away"]

                total = gh + ga

                if last_goals == -1:
                    last_goals = total

                if total > last_goals:
                    if (home_id == TEAM_ID and gh > ga) or \
                       (away_id == TEAM_ID and ga > gh):

                        print("GOOOOL DO PALMEIRAS!")
                        trigger()

                    last_goals = total

                print(f"Placar: {gh} x {ga}")
                time.sleep(20)

            else:
                print("Jogo ainda não começou ou terminou.")
                time.sleep(300)


# roda o monitor em paralelo
Thread(target=monitor).start()

# inicia servidor web (mantém Railway ativo)
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
