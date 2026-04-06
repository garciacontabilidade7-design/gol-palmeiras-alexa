import os
import requests
import time
from datetime import datetime, timedelta

# ---------------- CONFIGURAÇÃO ----------------
API_KEY = "8b785b51ef784e1bf47ebb1ac9796119"
TEMPORADA = 2026
CHECK_INTERVAL = 30  # segundos entre verificações

# Times do jogo específico
TIME_HOME = "US Lecce"
TIME_AWAY = "Atalanta"

# Voice Monkey
VOICE_TOKEN = os.environ.get("VOICE_TOKEN")
VOICE_MONKEY_URL = f"https://api.voicemonkey.io/trigger?token={VOICE_TOKEN}&monkey=gol"

# ---------------- FUNÇÃO PARA PEGAR JOGO ----------------
def pegar_jogo():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "v3.football.api-sports.io"
    }

    hoje = (datetime.utcnow() - timedelta(hours=3)).strftime("%Y-%m-%d")  # horário de Brasília
    SERIE_A_ID = 135  # ID da Serie A (Itália)

    params = {"league": SERIE_A_ID, "season": TEMPORADA, "date": hoje}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        fixtures = data.get("response", [])

        # DEBUG: mostrar todos os jogos retornados
        print("DEBUG - jogos retornados pela API:")
        for jogo in fixtures:
            home = jogo["teams"]["home"]["name"]
            away = jogo["teams"]["away"]["name"]
            status = jogo["fixture"]["status"]["short"]
            print(f"{home} x {away} - Status: {status}")

        # Procurar o jogo específico
        for jogo in fixtures:
            home = jogo["teams"]["home"]["name"]
            away = jogo["teams"]["away"]["name"]
            if home == TIME_HOME and away == TIME_AWAY:
                return jogo
        return None

    except Exception as e:
        print("Erro ao buscar jogo:", e)
        return None

# ---------------- FUNÇÃO PARA ALERTA VOICE MONKEY ----------------
def enviar_alerta_gol():
    try:
        requests.get(VOICE_MONKEY_URL)
        print("Gol detectado! Alerta enviado.")
    except Exception as e:
        print("Erro ao enviar alerta:", e)

# ---------------- LOOP PRINCIPAL ----------------
def monitorar_gols():
    ultimo_placar = None
    while True:
        jogo = pegar_jogo()
        if jogo:
            score = jogo["score"]["fulltime"]
            gols_home = score["home"] if score["home"] is not None else 0
            gols_away = score["away"] if score["away"] is not None else 0

            placar_atual = {"home": gols_home, "away": gols_away}

            if ultimo_placar:
                # detecta qualquer gol
                if placar_atual["home"] > ultimo_placar["home"] or placar_atual["away"] > ultimo_placar["away"]:
                    enviar_alerta_gol()

            ultimo_placar = placar_atual
        else:
            print("Jogo não encontrado ainda ou erro na API.")

        time.sleep(CHECK_INTERVAL)

# ---------------- EXECUÇÃO ----------------
if __name__ == "__main__":
    print("Monitoramento do jogo US Lecce x Atalanta iniciado...")
    monitorar_gols()
