import requests
from bs4 import BeautifulSoup
import time
import os

# --- CONFIGURAÇÕES ---
VOICE_TOKEN = os.environ.get("VOICE_TOKEN")  # token do Railway
VOICE_DEVICE = os.environ.get("VOICE_DEVICE")  # device ID do Voice Monkey

# URL do jogo específico (ajuste conforme o site que quiser)
# Exemplo: Globoesporte -> Lecce x Atalanta
JOGO_URL = "https://globoesporte.globo.com/futebol/italia/serie-a/jogo/2026-04-06/lecce-atalanta/"

# --- FUNÇÕES ---
def pegar_placar():
    """Faz scraping do placar do site e retorna (gols_home, gols_away)"""
    try:
        res = requests.get(JOGO_URL, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Globoesporte: busca elementos de gols
        home_score_elem = soup.find("span", {"class": "placar__time__gols-home"})
        away_score_elem = soup.find("span", {"class": "placar__time__gols-away"})
        
        if home_score_elem and away_score_elem:
            gols_home = int(home_score_elem.text.strip())
            gols_away = int(away_score_elem.text.strip())
            return (gols_home, gols_away)
        else:
            return None
    except Exception as e:
        print("Erro ao pegar placar:", e)
        return None

def enviar_alerta_gol():
    """Dispara alerta no Voice Monkey"""
    url = f"https://api.voicemonkey.io/trigger?AccessToken={VOICE_TOKEN}&Device={VOICE_DEVICE}&MonkeyType=smart&CustomMessage=Gol!"
    try:
        requests.get(url)
        print("Alerta de gol enviado!")
    except:
        print("Erro ao enviar alerta Voice Monkey")

# --- LOOP PRINCIPAL ---
ultimo_placar = None
print("Monitoramento do jogo Lecce x Atalanta iniciado...")
while True:
    placar = pegar_placar()
    if placar:
        if ultimo_placar is None:
            ultimo_placar = placar
        if placar != ultimo_placar:
            enviar_alerta_gol()
            ultimo_placar = placar
        print(f"Placar atual: {placar[0]} x {placar[1]}")
    else:
        print("Placar não disponível ainda.")
    
    time.sleep(30)  # verifica a cada 30 segundos
