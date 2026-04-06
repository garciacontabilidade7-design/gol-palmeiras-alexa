import requests
import time
import os
from threading import Thread
from flask import Flask

API_KEY = os.getenv("API_KEY")
VOICE_TOKEN = os.getenv("VOICE_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor ativo 🚀"


# 🔴 Busca TODOS jogos ao vivo
def get_live_match():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        jogos = data.get("response", [])

        if jogos:
            print(f"{len(jogos)} jogos ao vivo encontrados:")

            for j in jogos:
                home = j["teams"]["home"]["name"]
                away = j["teams"]["away"]["name"]
                print(f"➡️ {home} x {away}")

            return jogos[0]  # usa o primeiro jogo

    except Exception as e:
        print("Erro ao buscar jogos:", e)

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
        print("🔊 GOL DETECTADO! Alexa acionada!")
    except Exception as e:
        print("Erro Alexa:", e)


# 🧠 Monitor principal
def monitor():
    print("Modo TESTE iniciado...")

    last_goals = -1

    while True:

        print("Buscando jogos ao vivo...")

        live = get_live_match()

        if not live:
            print("Nenhum jogo ao vivo. Tentando em 5 minutos...")
            time.sleep(300)
            continue

        print("🔥 JOGO AO VIVO DETECTADO!")

        while True:
            live = get_live_match()

            if not live:
                print("🏁 Jogo terminou.")
                last_goals = -1
                break

            home = live["teams"]["home"]["name"]
            away = live["teams"]["away"]["name"]

            gh = live["goals"]["home"]
            ga = live["goals"]["away"]

            total = gh + ga

            if last_goals == -1:
                last_goals = total

            # ⚽ Detecta qualquer gol
            if total > last_goals:
                print(f"⚽ GOL! {home} {gh} x {ga} {away}")
                trigger()
                last_goals = total

            print(f"Placar: {home} {gh} x {ga} {away}")

            # ⏱️ consulta rápida pra teste
            time.sleep(15)


# 🚀 inicia monitor em paralelo
Thread(target=monitor).start()


# 🌐 servidor (Railway)
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
