import requests
import time
import os

API_KEY = os.getenv("API_KEY")
VOICE_TOKEN = os.getenv("VOICE_TOKEN")

TEAM_ID = 121  # Palmeiras

last_goals = -1


def get_live_match():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        for match in data.get("response", []):
            home_id = match["teams"]["home"]["id"]
            away_id = match["teams"]["away"]["id"]

            if TEAM_ID in [home_id, away_id]:
                return match

    except Exception as e:
        print("Erro API:", e)

    return None


def trigger_alexa():
    try:
        url = "https://api.voicemonkey.io/trigger"
        params = {
            "access_token": VOICE_TOKEN,
            "monkey": "gol_palmeiras"
        }

        requests.get(url, params=params, timeout=5)
        print("Disparou Alexa!")

    except Exception as e:
        print("Erro ao disparar:", e)


print("Monitorando jogo do Palmeiras...")

while True:
    match = get_live_match()

    if match:
        home_id = match["teams"]["home"]["id"]
        away_id = match["teams"]["away"]["id"]

        home_goals = match["goals"]["home"]
        away_goals = match["goals"]["away"]

        total_goals = home_goals + away_goals

        if last_goals == -1:
            last_goals = total_goals

        # Detecta novo gol
        if total_goals > last_goals:

            # Verifica se foi gol do Palmeiras
            if (home_id == TEAM_ID and home_goals > away_goals) or \
               (away_id == TEAM_ID and away_goals > home_goals):

                print("GOOOOOOL DO PALMEIRAS!")
                trigger_alexa()

            else:
                print("Gol, mas não foi do Palmeiras")

            last_goals = total_goals

        print(f"Placar: {home_goals} x {away_goals}")

    else:
        print("Nenhum jogo ao vivo do Palmeiras")

    time.sleep(15)
