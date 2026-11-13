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

# Bandeiras personalizadas (garante o padrão visual do seu painel)
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
        # Consulta diretamente a API oficial de placares da ESPN para amistosos internacionais
        # O parâmetro dates busca a janela de jogos de novembro de 2026
        espn_url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.friendly/scoreboard?dates=20261113-20261120"
        response = requests.get(espn_url, timeout=10)
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
            
            # Identifica mandante (home) e visitante (away)
            home_comp = next((c for c in competitors if c.get("homeAway") == "home"), None)
            away_comp = next((c for c in competitors if c.get("homeAway") == "away"), None)

            if not home_comp or not away_comp:
                continue

            home_name_en = home_comp["team"].get("name", "")
            away_name_en = away_comp["team"].get("name", "")

            # Filtra apenas os confrontos envolvendo a Seleção Brasileira
            if "Brazil" not in [home_name_en, away_name_en]:
                continue

            home_team = TRADUCAO_TIMES.get(home_name_en, home_name_en)
            away_team = TRADUCAO_TIMES.get(away_name_en, away_name_en)

            # Placares reais vindos da ESPN
            home_score = int(home_comp.get("score", 0))
            away_score = int(away_comp.get("score", 0))

            # Conversão da data/hora UTC da ESPN para Horário de Brasília (-03:00)
            date_str_utc = event.get("date") # Ex: "2026-11-14T10:15Z"
            match_time_utc = datetime.fromisoformat(date_str_utc.replace("Z", "+00:00"))
            match_time_br = match_time_utc.astimezone(fuso_br)

            # Formatação amigável da data
            dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
            dia_str = dias_semana[match_time_br.weekday()]
            data_formatada = f"{dia_str}, {match_time_br.strftime('%d/%m/%Y às %H:%M')}"

            # Padronização do Estádio
            venue_name = comp.get("venue", {}).get("fullName", "Estádio Nacional de Singapura")
            if "National Stadium" in venue_name or "Estádio Nacional" in venue_name:
                venue_name = "Estádio Nacional de Singapura"

            # Status real da ESPN + Regra dos 10 minutos antes para Ao Vivo
            espn_state = event.get("status", {}).get("type", {}).get("state", "pre") # pre, in, post
            match_clock = event.get("status", {}).get("displayClock", "") # Ex: "45'+2'" ou "68'"
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

        return jogos_filtrados

    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erro ao conectar na ESPN: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
