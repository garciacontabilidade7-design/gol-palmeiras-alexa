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


# 🔥 PEGA PRÓXIMO JOGO (SEM USAR DATA)
def get_next_match():
    url = f"https://v3.football.api-sports.io/fixtures?team={TEAM_ID}&next=1"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        if data["response"]:
            return data["response"][0]

    except Exception as e:
        print("Erro ao buscar próximo jogo:", e)

    return None


# 🔥 PEGA JOGO AO VIVO
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


# 🔊 DISPARA ALEXA
def trigger():
    if not VOICE_TOKEN:
        print("VOICE_TOKEN não configurado")
        return

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
        print("Erro ao disparar Alexa:", e)


# 🧠 MONITOR INTELIGENTE
def monitor():
    print("Sistema inteligente iniciado...")

    last_goals = -1

    while True:
        match = get_next_match()

        if not match:
            print("Erro ao buscar próximo jogo. Tentando em 10min...")
            time.sleep(600)
            continue

        # ⏰ horário do jogo (UTC → Brasil)
        match_time_utc = datetime.fromisoformat(match["fixture"]["date"].replace("Z", "+00:00"))
        match_time_br = match_time_utc - timedelta(hours=3)

        now = datetime.now(UTC) - timedelta(hours=3)

        diff = (match_time_br - now).total_seconds()

        print(f"Próximo jogo às {match_time_br.strftime('%d/%m %H:%M')}")

        # 🔥 Se faltar mais de 2h → dorme
        if diff > 7200:
            print("Jogo ainda longe. Dormindo 30min...")
            time.sleep(1800)
            continue

        print("Jogo próximo! Monitorando ao vivo...")

        # 🔥 MONITORAR AO VIVO
        while True:
            live = get_live_match()

            if live:
                home_id = live["teams"]["home"]["id"]
                away_id = live["teams"]["away"]["id"]

                gh = live["goals"]["home"]
                ga = live["goals"]["away"]

                total = gh + ga

                if last_goals == -1:
                    last_goals = total

                if total > last_goals:
                    # ⚽ verifica se foi gol do Palmeiras
                    if (home_id == TEAM_ID and gh > ga) or \
                       (away_id == TEAM_ID and ga > gh):

                        print("GOOOOL DO PALMEIRAS!")
                        trigger()

                    last_goals = total

                print(f"Placar: {gh} x {ga}")
                time.sleep(20)

            else:
                print("Aguardando jogo começar...")
                time.sleep(60)


# 🚀 THREAD DO MONITOR
Thread(target=monitor).start()


# 🌐 SERVIDOR WEB (Railway)
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
