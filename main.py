from flask import Flask, jsonify
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# ---------------- CONFIGURAÇÃO ----------------
API_KEY = "8b785b51ef784e1bf47ebb1ac9796119"  # chave da API-Football
API_HOST = "v3.football.api-sports.io"
LA_LIGA_ID = 140  # ID da La Liga na API-Football
HORARIO_JOGO = 16  # horário de Brasília que você quer monitorar (16h)
TIMEZONE = "America/Sao_Paulo"
TEMPORADA = 2026  # temporada atual da API

# ----------------- FUNÇÃO DE DADOS GOOGLE -----------------
def pegar_dados_google():
    # Aqui você pode implementar scraping do Google
    # Por enquanto vamos simular tentativa que falha
    return None

# ----------------- FUNÇÃO DE DADOS API-Football (fallback) -----------------
def pegar_dados_api_football():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    # Filtrando apenas jogos da La Liga hoje
    brasilia = pytz.timezone(TIMEZONE)
    hoje = datetime.now(brasilia).strftime("%Y-%m-%d")
    params = {
        "league": LA_LIGA_ID,
        "season": TEMPORADA,
        "date": hoje
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        fixtures = data.get("response", [])

        if not fixtures:
            return "Não há jogos da La Liga hoje."

        resultados = []
        for jogo in fixtures:
            fixture = jogo["fixture"]
            teams = jogo["teams"]
            score = jogo["score"]["fulltime"]

            home = teams["home"]["name"]
            away = teams["away"]["name"]
            status = fixture["status"]["short"]
            score_str = f"{score['home']} x {score['away']}" if score["home"] is not None else "Ainda não começou"

            resultados.append(f"{home} x {away} - Status: {status}, Placar: {score_str}")

        return "\n".join(resultados)

    except Exception as e:
        return f"Erro ao buscar dados da API-Football: {e}"

# ----------------- ROTA FLASK -----------------
@app.route("/monitorar")
def monitorar_jogo():
    brasilia = pytz.timezone(TIMEZONE)
    agora = datetime.now(brasilia)

    if agora.hour < HORARIO_JOGO:
        return jsonify({"mensagem": "Os jogos da La Liga ainda não começaram. Volte às 16h."})

    # Tenta pegar do Google
    dados = pegar_dados_google()
    if not dados:
        # Se falhar, pega da API-Football
        dados = pegar_dados_api_football()

    return jsonify({"mensagem": dados})

# ----------------- INICIALIZAÇÃO -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
