import requests
import time
from datetime import datetime
import os

# --- CONFIGURAÇÕES ---
API_FOOTBALL_KEY = "8b785b51ef784e1bf47ebb1ac9796119"
VOICE_TOKEN = os.environ.get("VOICE_TOKEN")  # token do Railway
VOICE_DEVICE = os.environ.get("VOICE_DEVICE")  # device ID do Voice Monkey

# IDs dos times
TEAM1_ID = 867  # Lecce
TEAM2_ID = 499  # Atalanta

# Liga e temporada (opcional, para filtrar se quiser)
LEAGUE_ID = 195  # Exemplo: Serie A 2025/26
SEASON = 2025

# --- FUNÇÕES ---
def get_fixture():
    """Busca o jogo de hoje entre os dois times."""
    hoje = datetime.utcnow().strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?team={TEAM1_ID}&date={hoje}"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": "v3.football.api-sports.io"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        fixtures = data.get("response", [])
        for f in fixtures:
            teams = f["teams"]
            if teams["home"]["id"] == TEAM1_ID and teams["away"]["id"] == TEAM2_ID or \
               teams["home"]["id"] == TEAM2_ID and teams["away"]["id"] == TEAM1_ID:
                return f  # retorna o fixture do jogo
        return None
    except Exception as e:
        print("Erro na API:", e)
        return None

def enviar_alerta_gol():
    """Dispara alerta no Voice Monkey"""
    url = f"https://api.voicemonkey.io/trigger?AccessToken={VOICE_TOKEN}&Device={VOICE_DEVICE}&MonkeyType=smart&CustomMessage=Gol!"
    try:
        requests.get(url)
        print("Alerta de gol enviado!")
    except:
        print("Erro ao enviar alerta Voice Monkey")

# --- MAIN LOOP ---
ultimo_placar = None
print("Monitoramento do jogo Lecce x Atalanta iniciado...")
while True:
    fixture = get_fixture()
    if fixture:
        goals_home = fixture["goals"]["home"]
        goals_away = fixture["goals"]["away"]
        placar_atual = (goals_home, goals_away)
        if ultimo_placar is None:
            ultimo_placar = placar_atual
        # Se houve gol desde a última verificação
        if placar_atual != ultimo_placar:
            enviar_alerta_gol()
            ultimo_placar = placar_atual
        print(f"Placar: {goals_home} x {goals_away}")
    else:
        print("Jogo não encontrado ainda ou erro na API.")
    time.sleep(30)  # verifica a cada 30 segundos
