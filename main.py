
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bandeiras personalizadas redondas
BANDEIRAS_CUSTOM = {
    "Brazil": "https://i.postimg.cc/1zwFGLvM/crie-uma-identidade-visual-exclusiva-baseada-na-ba-removebg-preview.png",
    "Brasil": "https://i.postimg.cc/1zwFGLvM/crie-uma-identidade-visual-exclusiva-baseada-na-ba-removebg-preview.png",
    "Japan": "https://i.postimg.cc/ydnknBcf/pngtree-japan-national-flag-round-shape-png-image-6589986.png",
    "Japão": "https://i.postimg.cc/ydnknBcf/pngtree-japan-national-flag-round-shape-png-image-6589986.png",
    "Singapore": "https://i.postimg.cc/fRtW8f54/bandeira-removebg-preview.png",
    "Singapura": "https://i.postimg.cc/fRtW8f54/bandeira-removebg-preview.png"
}

TRADUCAO_TIMES = {
    "Brazil": "Brasil",
    "Japan": "Japão",
    "Singapore": "Singapura"
}

@app.get("/api/selecao/jogos")
def get_jogos_selecao():
    fuso_br = timezone(timedelta(hours=-3))
    now = datetime.now(fuso_br)
    jogos_filtrados = []

    try:
        # Endpoint oficial da ESPN para amistosos internacionais com User-Agent
        espn_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.friendly/scoreboard"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(espn_url, headers=headers, timeout=5)
        if response.status_code == 200:
            dados_espn = response.json()

            for event in dados_espn.get("events", []):
                competitions = event.get("competitions", [])
                if not competitions:
                    continue
                
                comp = competitions[0]
                competitors = comp.get("competitors", [])
                
                home_comp = next((c for c in competitors if c.get("homeAway") == "home"), None)
                away_comp = next((c for c in competitors if c.get("homeAway") == "away"), None)

                if not home_comp or not away_comp:
                    continue

                home_name_en = home_comp["team"].get("name", "")
                away_name_en = away_comp["team"].get("name", "")

                if "Brazil" not in [home_name_en, away_name_en] and "Brasil" not in [home_name_en, away_name_en]:
                    continue

                home_team = TRADUCAO_TIMES.get(home_name_en, home_name_en)
                away_team = TRADUCAO_TIMES.get(away_name_en, away_name_en)

                home_score = int(home_comp.get("score", 0))
                away_score = int(away_comp.get("score", 0))

                date_str_utc = event.get("date")
                match_time_utc = datetime.fromisoformat(date_str_utc.replace("Z", "+00:00"))
                match_time_br = match_time_utc.astimezone(fuso_br)

                dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
                dia_str = dias_semana[match_time_br.weekday()]
                data_formatada = f"{dia_str}, {match_time_br.strftime('%d/%m/%Y às %H:%M')}"

                venue_name = "Estádio Nacional de Singapura"

                espn_state = event.get("status", {}).get("type", {}).get("state", "pre")
                match_clock = event.get("status", {}).get("displayClock", "")
                live_start = match_time_br - timedelta(minutes=10)
                match_end = match_time_br + timedelta(hours=2)

                if espn_state == "post":
                    status = "ENCERRADO"
                elif espn_state == "in" or (match_time_br <= now <= match_end) or (now >= live_start and now < match_time_br):
                    status = "AO VIVO"
                else:
                    status = "PRE"

                jogos_filtrados.append({
                    "id": event.get("id"),
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_flag": BANDEIRAS_CUSTOM.get(home_name_en, home_comp["team"].get("logo")),
                    "away_flag": BANDEIRAS_CUSTOM.get(away_name_en, away_comp["team"].get("logo")),
                    "home_score": home_score,
                    "away_score": away_score,
                    "match_clock": match_clock if espn_state == "in" else "",
                    "status": status,
                    "date": data_formatada,
                    "timestamp": match_time_br.strftime("%Y-%m-%dT%H:%M:%S"),
                    "stadium": venue_name,
                    "sub_info": "Jogo amistoso",
                    "competition": "Amistoso Internacional"
                })
        
        # Fallback estruturado com o horário corrigido cravado em 07:15
        if not jogos_filtrados:
            jogos_base = [
                {
                    "id": "1",
                    "home_team": "Brasil",
                    "away_team": "Japão",
                    "home_flag": BANDEIRAS_CUSTOM["Brasil"],
                    "away_flag": BANDEIRAS_CUSTOM["Japão"],
                    "home_score": 0,
                    "away_score": 0,
                    "match_clock": "",
                    "status": "PRE",
                    "date": "Sábado, 14/11/2026 às 07:15",
                    "timestamp": "2026-11-14T07:15:00",
                    "stadium": "Estádio Nacional de Singapura",
                    "sub_info": "Jogo amistoso",
                    "competition": "Amistoso Internacional"
                },
                {
                    "id": "2",
                    "home_team": "Singapura",
                    "away_team": "Brasil",
                    "home_flag": BANDEIRAS_CUSTOM["Singapura"],
                    "away_flag": BANDEIRAS_CUSTOM["Brasil"],
                    "home_score": 0,
                    "away_score": 0,
                    "match_clock": "",
                    "status": "PRE",
                    "date": "Terça-feira, 17/11/2026 às 07:00",
                    "timestamp": "2026-11-17T07:00:00",
                    "stadium": "Estádio Nacional de Singapura",
                    "sub_info": "Jogo amistoso",
                    "competition": "Amistoso Internacional"
                }
            ]

            for jogo in jogos_base:
                match_time = datetime.fromisoformat(jogo["timestamp"]).replace(tzinfo=fuso_br)
                live_start = match_time - timedelta(minutes=10)
                match_end = match_time + timedelta(hours=2)

                if now < live_start:
                    status = "PRE"
                elif live_start <= now <= match_end:
                    status = "AO VIVO"
                else:
                    status = "ENCERRADO"

                j_copy = jogo.copy()
                j_copy["status"] = status
                jogos_filtrados.append(j_copy)

        return jogos_filtrados

    except Exception as e:
        return [
            {
                "id": "1",
                "home_team": "Brasil",
                "away_team": "Japão",
                "home_flag": BANDEIRAS_CUSTOM["Brasil"],
                "away_flag": BANDEIRAS_CUSTOM["Japão"],
                "home_score": 0,
                "away_score": 0,
                "match_clock": "",
                "status": "PRE",
                "date": "Sábado, 14/11/2026 às 07:15",
                "timestamp": "2026-11-14T07:15:00",
                "stadium": "Estádio Nacional de Singapura",
                "sub_info": "Jogo amistoso",
                "competition": "Amistoso Internacional"
            },
            {
                "id": "2",
                "home_team": "Singapura",
                "away_team": "Brasil",
                "home_flag": BANDEIRAS_CUSTOM["Singapura"],
                "away_flag": BANDEIRAS_CUSTOM["Brasil"],
                "home_score": 0,
                "away_score": 0,
                "match_clock": "",
                "status": "PRE",
                "date": "Terça-feira, 17/11/2026 às 07:00",
                "timestamp": "2026-11-17T07:00:00",
                "stadium": "Estádio Nacional de Singapura",
                "sub_info": "Jogo amistoso",
                "competition": "Amistoso Internacional"
            }
        ]
