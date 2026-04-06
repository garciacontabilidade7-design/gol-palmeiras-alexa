import requests
from bs4 import BeautifulSoup
import time
import os

# Configurações Voice Monkey
VOICE_TOKEN = os.environ.get("VOICE_TOKEN")
VOICE_DEVICE = os.environ.get("VOICE_DEVICE")

# Pesquisa Google para o jogo Lecce x Atalanta
GOOGLE_SEARCH = "US Lecce vs Atalanta placar ao vivo"

def pegar_placar_google():
    """Faz scraping do Google para pegar o placar"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        url = f"https://www.google.com/search?q={GOOGLE_SEARCH.replace(' ', '+')}"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Google costuma colocar o placar em spans com id "vs_c"
        home_score_elem = soup.find("div", class_="imso_mh__l-tm-sc")
        away_score_elem = soup.find("div", class_="imso_mh__r-tm-sc")
        
        if home_score_elem and away_score_elem:
            gols_home = int(home_score_elem.text.strip())
            gols_away = int(away_score_elem.text.strip())
            return (gols_home, gols_away)
        else:
            return None
    except Exception as e:
        print("Erro ao pegar placar do Google:", e)
        return None

def enviar_alerta_gol():
    url = f"https://api.voicemonkey.io/trigger?AccessToken={VOICE_TOKEN}&Device={VOICE_DEVICE}&MonkeyType=smart&CustomMessage=Gol!"
    try:
        requests.get(url)
        print("Alerta de gol enviado!")
    except:
        print("Erro ao enviar alerta Voice Monkey")

ultimo_placar = None
print("Monitoramento do jogo Lecce x Atalanta iniciado (Google)...")
while True:
    placar = pegar_placar_google()
    if placar:
        if ultimo_placar is None:
            ultimo_placar = placar
        if placar != ultimo_placar:
            enviar_alerta_gol()
            ultimo_placar = placar
        print(f"Placar atual: {placar[0]} x {placar[1]}")
    else:
        print("Placar ainda não disponível.")
    time.sleep(30)
