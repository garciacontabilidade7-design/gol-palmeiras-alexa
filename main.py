import requests
import time
import os
from threading import Thread
from flask import Flask

VOICE_TOKEN = os.getenv("VOICE_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor ativo 🚀"


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
        print("🔊 GOL SIMULADO! Alexa acionada!")
    except Exception as e:
        print("Erro Alexa:", e)


# 🧪 SIMULADOR DE GOL
def simulador():
    print("🧪 Modo SIMULAÇÃO iniciado...")

    while True:
        print("⏳ Aguardando próximo gol...")
        time.sleep(30)  # intervalo

        print("⚽ SIMULANDO GOL!!!")
        trigger()


# 🚀 inicia simulador
Thread(target=simulador).start()


# 🌐 servidor (Railway)
port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port)
