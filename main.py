from datetime import datetime, timedelta
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Importe sua sessão de banco e modelos (conforme o seu database.py e models.py)
# from database import get_db
# import models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/selecao/jogos")
def get_jogos_selecao(db: Session = Depends(get_db)):
    # 1. Busca os jogos diretamente da fonte de dados (banco de dados)
    # Exemplo: jogos_db = db.query(models.Partida).all()
    
    # 2. Se estiver usando os dados simulados mas quiser que eles venham dinamicamente:
    now = datetime.now()
    
    # (Lista de jogos recuperada da fonte de dados)
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
            "competition": "Amistoso Internacional",
            "home_score": 0,  # Dados vindos da fonte
            "away_score": 0   # Dados vindos da fonte
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
            "competition": "Amistoso Internacional",
            "home_score": 0,
            "away_score": 0
        }
    ]

    # Aplica a automação temporal em cima dos dados retornados pela fonte
    for jogo in jogos:
        match_time = datetime.fromisoformat(jogo["timestamp"])
        live_start = match_time - timedelta(minutes=10)
        match_end = match_time + timedelta(hours=2)

        if now < live_start:
            jogo["status"] = "PRE"
        elif live_start <= now <= match_end:
            jogo["status"] = "AO VIVO"
        else:
            jogo["status"] = "ENCERRADO"

    return jogos
