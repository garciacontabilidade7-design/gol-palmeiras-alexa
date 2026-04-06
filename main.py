import requests
import time
import os
from threading import Thread
from flask import Flask
from datetime import datetime

API_KEY = os.getenv("API_KEY")
VOICE_TOKEN = os.getenv("VOICE_TOKEN")

TEAM_ID = 121  # Palmeiras

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor ativo 🚀"


# 🔍 Busca jogo do dia
def get_today_match():
    today = datetime.utcnow().strftime('%Y-%m-%d')

    url = f"https://v3.football.api-sports.io/fixtures?team={TEAM_ID}&date={today}"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        if data.get("response"):
            return data["response"][0]

    except Exception as e:
        print("Erro ao buscar jogo:", e)

    return None


# 🔴 Jogo ao vivo
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


# 🔊 Dispara Alexa
def trigger():
    try:
        requests.get(
            "https://api-v2.voicemonkey.io/trigger",
            params={
                "token": VOICE_TOKEN,
                "device": "golpalmeiras"
            },
            timeout=5
        )
        print("Disparou Alexa!")
    except Exception as e:
        print("Erro Alexa:", e)


# 🧠 Monitor principal
def monitor():
    print("Sistema inteligente iniciado...")

    last_goals = -1
    jogo_detectado = False

    while True:
        # 🧊 Verifica só 2x por dia
        if not jogo_detectado:
            print("Verificando se tem jogo hoje...")

            match = get_today_match()

            if match:
                print("Tem jogo hoje! Aguardando início...")
                jogo_detectado = True
            else:
                print("Sem jogo hoje. Próxima checagem em 12h...")
                time.sleep(43200)
                continue

        # ⏳ Espera começar
        live = get_live_match()

        if not live:
            print("Jogo ainda não começou...")
            time.sleep(300)  # 5 min
            continue

        print("⚽ JOGO AO VIVO! Monitorando...")

        # ⚡ Durante o jogo
        while True:
            live = get_live_match()

            if not live:
                print("Jogo terminou.")
                last_goals = -1
                jogo_detectado = False
                break

            home_id = live["teams"]["home"]["id"]
            away_id = live["teams"]["away"]["id"]

            gh = live["goals"]["home"]
            ga = live["goals"]["away"]

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

            # ⏱️ 30 segundos (SEU PEDIDO)
            time.sleep(30)


Thread(target=monitor).start()

port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
