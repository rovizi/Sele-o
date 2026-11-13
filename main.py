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
    try:
        # URL geral de placares da ESPN com User-Agent para evitar bloqueio 400
        espn_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/scoreboard?dates=20261113-20261120"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(espn_url, headers=headers, timeout=10)
        response.raise_for_status()
        dados_espn = response.json()

        jogos_filtrados = []
        fuso_br = timezone(timedelta(hours=-3))
        now = datetime.now(fuso_br)

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

            # Padronização forçada para ambos os jogos exibirem o nome completo
            venue_name = comp.get("venue", {}).get("fullName", "")
            if not venue_name or "National Stadium" in venue_name or "Estádio Nacional" in venue_name:
                venue_name = "Estádio Nacional de Singapura"

            espn_state = event.get("status", {}).get("type", {}).get("state", "pre")
            match_clock = event.get("status", {}).get("displayClock", "")
            live_start = match_time_br - timedelta(minutes=10)

            if espn_state == "post":
                status = "ENCERRADO"
            elif espn_state == "in" or (espn_state == "pre" and now >= live_start):
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

        # Fallback: Se a ESPN ainda não tiver indexado a partida no feed público, garante que os dois jogos aparecem perfeitamente
        if not jogos_filtrados:
            jogos_filtrados = [
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

        return jogos_filtrados

    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao conectar na ESPN: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
