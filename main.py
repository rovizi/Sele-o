from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuração de CORS para permitir a comunicação com o front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/selecao/jogos")
def get_jogos_selecao():
    now = datetime.now()
    
    jogos = [
        {
            "id": 1,
            "home_team": "Brasil",
            "away_team": "Japão",
            "home_flag": "https://i.postimg.cc/1zwFGLvM/crie-uma-identidade-visual-exclusiva-baseada-na-ba-removebg-preview.png",
            "away_flag": "https://i.postimg.cc/ydnknBcf/pngtree-japan-national-flag-round-shape-png-image-6589986.png",
            "date": "Sábado, 14/11/2026 às 07:15",
            "timestamp": "2026-11-14T07:15:00",
            "stadium": "Estádio Nacional de Singapura",
            "sub_info": "Jogo amistoso",
            "competition": "Amistoso Internacional"
        },
        {
            "id": 2,
            "home_team": "Singapura",
            "away_team": "Brasil",
            "home_flag": "https://i.postimg.cc/fRtW8f54/bandeira-removebg-preview.png",
            "away_flag": "https://i.postimg.cc/1zwFGLvM/crie-uma-identidade-visual-exclusiva-baseada-na-ba-removebg-preview.png",
            "date": "Terça-feira, 17/11/2026 às 07:00",
            "timestamp": "2026-11-17T07:00:00",
            "stadium": "Estádio Nacional de Singapura",
            "sub_info": "Jogo amistoso",
            "competition": "Amistoso Internacional"
        }
    ]

    # Lógica automatizada de status baseada no horário atual
    for jogo in jogos:
        match_time = datetime.fromisoformat(jogo["timestamp"])
        
        # O jogo entra ao vivo 10 minutos antes da hora marcada
        live_start = match_time - timedelta(minutes=10)
        
        # Consideramos que o jogo dura cerca de 2 horas até encerrar
        match_end = match_time + timedelta(hours=2)

        if now < live_start:
            jogo["status"] = "PRE"       # Agendado / Pré-jogo
        elif live_start <= now <= match_end:
            jogo["status"] = "AO VIVO"   # Rola 10 min antes até 2h depois
        else:
            jogo["status"] = "ENCERRADO" # Após 2h do início

    return jogos
