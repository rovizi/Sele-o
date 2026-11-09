from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import urllib.request
import json
from datetime import datetime, timezone, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definição do fuso horário de Brasília (UTC-3)
BRT = timezone(timedelta(hours=-3))

# URL da API da ESPN para partidas internacionais
ESPN_SELECAO_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fif.friendlies/scoreboard"

# Mapeamento local fixo de bandeiras controladas pela sua API
BANDEIRAS_SELECOES = {
    "Brazil": "https://i.postimg.cc/1zwFGLvM/crie-uma-identidade-visual-exclusiva-baseada-na-ba-removebg-preview.png",
    "Brasil": "https://i.postimg.cc/1zwFGLvM/crie-uma-identidade-visual-exclusiva-baseada-na-ba-removebg-preview.png",
    "Japan": "https://i.postimg.cc/ydnknBcf/pngtree-japan-national-flag-round-shape-png-image-6589986.png",
    "Japão": "https://i.postimg.cc/ydnknBcf/pngtree-japan-national-flag-round-shape-png-image-6589986.png"
}

def obter_bandeira(nome_time):
    """Retorna a bandeira fixa da API ou uma imagem padrão caso não encontre."""
    return BANDEIRAS_SELECOES.get(nome_time, "https://i.postimg.cc/c4mpD6zM/bola-removebg-preview.png")

def fetch_espn_data(url):
    """Busca dados da ESPN usando urllib nativo do Python."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Erro na requisição ESPN Seleção: {e}")
    return {}

def parse_espn_matches(data):
    """Processa o JSON da ESPN no formato padrão do backend da seleção."""
    matches = []
    if not data or not isinstance(data, dict) or "events" not in data:
        return matches

    for i, event in enumerate(data.get("events", [])):
        try:
            match_id = str(event.get("id", i + 1))
            name = event.get("name", "")
            date_str = event.get("date", "")
            
            status_info = event.get("status", {})
            status_type = status_info.get("type", {})
            state = status_type.get("state", "pre")
            
            status_code = "LIVE" if state == "in" else status_type.get("state", "pre").upper()
            status_detail = status_type.get("detail") or status_type.get("description", "")
            
            competitions = event.get("competitions", [])
            if not competitions:
                continue
                
            competition = competitions[0]
            competitors = competition.get("competitors", [])
            
            home_team = None
            away_team = None
            
            for comp in competitors:
                team_data = comp.get("team", {})
                team_name = team_data.get("displayName") or team_data.get("name", "Seleção")
                team_logo = obter_bandeira(team_name)
                
                team_info = {
                    "name": team_name,
                    "logo": team_logo,
                    "score": str(comp.get("score", "0"))
                }
                if comp.get("homeAway") == "home":
                    home_team = team_info
                else:
                    away_team = team_info

            matches.append({
                "id": match_id,
                "name": name,
                "date": date_str,
                "status": status_code,
                "status_text": status_detail,
                "home_team": home_team,
                "away_team": away_team,
                "campeonato": competition.get("type", {}).get("text", "Amistoso Internacional"),
                "estadio": "Estádio Nacional de Singapura"
            })
        except Exception:
            continue

    return matches

@app.get("/")
def read_root():
    return {
        "message": "API da Seleção (Live Goal) integrada com ESPN e assets locais!",
        "status": "online",
    }

@app.get("/api/selecao/jogos")
def get_jogos_selecao():
    try:
        raw_data = fetch_espn_data(ESPN_SELECAO_URL)
        matches = parse_espn_matches(raw_data)
        
        # Override manual para o jogo do Brasil x Japão (14/11/2026 às 07:15)
        manual_match_brasil_japao = {
            "id": "bra_jpn_2026",
            "name": "Brazil vs Japan",
            "home_team": {
                "name": "Brasil",
                "logo": obter_bandeira("Brasil"),
                "score": "0"
            },
            "away_team": {
                "name": "Japão",
                "logo": obter_bandeira("Japão"),
                "score": "0"
            },
            "status": "PRE",
            "status_text": "07:15",
            "date": "2026-11-14T07:15:00-03:00",
            "timestamp": int(datetime(2026, 11, 14, 7, 15, tzinfo=BRT).timestamp()),
            "campeonato": "Amistoso Internacional",
            "estadio": "Estádio Nacional de Singapura"
        }
        
        if not any("Brazil" in m.get("name", "") and "Japan" in m.get("name", "") for m in matches):
            matches.insert(0, manual_match_brasil_japao)
            
        return matches
    except Exception as e:
        print(f"Erro em obter_jogos_selecao: {e}")
        return [
            {
                "id": "bra_jpn_2026",
                "name": "Brazil vs Japan",
                "home_team": {
                    "name": "Brasil",
                    "logo": obter_bandeira("Brasil"),
                    "score": "0"
                },
                "away_team": {
                    "name": "Japão",
                    "logo": obter_bandeira("Japão"),
                    "score": "0"
                },
                "status": "PRE",
                "status_text": "07:15",
                "date": "2026-11-14T07:15:00-03:00",
                "timestamp": int(datetime(2026, 11, 14, 7, 15, tzinfo=BRT).timestamp()),
                "campeonato": "Amistoso Internacional",
                "estadio": "Estádio Nacional de Singapura"
            }
        ]
