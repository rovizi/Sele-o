from fastapi import FastAPI
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


@app.get("/")
def read_root():
    return {
        "message": "API do Live Goal integrada com dados externos!",
        "status": "online",
    }


@app.get("/api/selecao/jogos")
def get_jogos_selecao():
    try:
        # Consulta à API pública de esportes em JSON (TheSportsDB)
        url = "https://www.thesportsdb.com/api/v1/json/3/searchevents.php?e=Brazil"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            eventos = data.get("event", [])
            
            if eventos:
                jogos_formatados = []
                for i, evento in enumerate(eventos[:5]):
                    jogos_formatados.append({
                        "id": i + 1,
                        "selecao": evento.get("strHomeTeam", "Brasil"),
                        "adversario": evento.get("strAwayTeam", "Adversário"),
                        "data": evento.get("dateEvent", "2026-09-25"),
                        "horario": evento.get("strTime", "Ao Vivo"),
                        "placar": f"{evento.get('intHomeScore', '0')} x {evento.get('intAwayScore', '0')}",
                        "status": "Ao Vivo" if evento.get("intHomeScore") else "Agendados",
                        "campeonato": evento.get("strLeague", "Partida Internacional"),
                    })
                return jogos_formatados

    except Exception as e:
        print(f"Erro ao consultar API externa: {e}")

    # Fallback seguro caso a API externa sofra instabilidade momentânea
    return [{
        "id": 1,
        "selecao": "Brasil",
        "adversario": "Colômbia",
        "data": "2026-09-25",
        "horario": "Ao Vivo",
        "placar": "3 x 0",
        "status": "Ao Vivo",
        "campeonato": "Eliminatórias / Amistoso",
    }]
