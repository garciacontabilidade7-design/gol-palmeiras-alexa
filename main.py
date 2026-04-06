import requests
import time
import os
from threading import Thread
from flask import Flask

API_KEY = os.getenv("API_KEY")
VOICE_TOKEN = os.getenv("VOICE_TOKEN")

TEAM_ID = 121  # Palmeiras

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor ativo 🚀"


# 🔴 Busca jogo AO VIVO (mais confiável)
def get_live_match():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        print("Consultando jogos ao vivo...")

        for m in data.get("response", []):
            home = m["teams"]["home"]["id"]
            away = m["teams"]["away"]["id"]

            if TEAM_ID in [home, away]:
                print("⚽ Palmeiras está jogando AO VIVO!")
                return m

    except Exception as e:
        print("Erro live:", e)

    return None


# 🔊 Disparo Alexa
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
        print("🔊 Gol enviado para Alexa!")
    except Exception as e:
        print("Erro Alexa:", e)


# 🧠 Monitor principal
def monitor():
    print("Sistema inteligente iniciado...")

    last_goals = -1

    while True:

        # 🧊 ECONOMIA: espera até ter jogo AO VIVO
        print("Verificando se Palmeiras está jogando...")

        live = get_live_match()

        if not live:
            print("Sem jogo ao vivo. Próxima tentativa em 30 minutos...")
            time.sleep(1800)  # 30 min
            continue

        print("🔥 JOGO AO VIVO DETECTADO!")

        # ⚡ MONITOR DURANTE O JOGO
        while True:
            live = get_live_match()

            if not live:
                print("🏁 Jogo terminou.")
                last_goals = -1
                break

            home_id = live["teams"]["home"]["id"]
            away_id = live["teams"]["away"]["id"]

            gh = live["goals"]["home"]
            ga = live["goals"]["away"]

            total = gh + ga

            if last_goals == -1:
                last_goals = total

            # ⚽ Detecta gol
            if total > last_goals:

                if (home_id == TEAM_ID and gh > ga) or \
                   (away_id == TEAM_ID and ga > gh):

                    print("GOOOOL DO PALMEIRAS!")
                    trigger()

                else:
                    print("Gol, mas não foi do Palmeiras.")

                last_goals = total

            print(f"Placar atual: {gh} x {ga}")

            # ⏱️ consulta a cada 30s (seguro pro limite)
            time.sleep(30)


# 🚀 inicia monitor em paralelo
Thread(target=monitor).start()


# 🌐 servidor (Railway)
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
