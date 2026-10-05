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
        "message": "API do Live Goal integrada e formatada!",
        "status": "online",
    }

@app.get("/api/selecao/jogos")
def get_jogos_selecao():
    try:
        url = "https://www.thesportsdb.com/api/v1/json/3/searchevents.php?e=Brazil"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            eventos = data.get("event", [])
            
            if eventos:
                jogos_formatados = []
                for i, evento in enumerate(eventos[:5]):
                    score_home = evento.get("intHomeScore")
                    score_away = evento.get("intAwayScore")
                    
                    raw_status = str(evento.get("strStatus", "")).strip().lower()
                    
                    # Trata o placar quando o jogo tem gols ou pontuação registrada
                    if score_home is not None and score_away is not None and score_home != "" and score_away != "":
                        placar = f"{score_home} x {score_away}"
                        
                        # Mapeamento inteligente de status da partida corrigido:
                        # Se explicitamente indica fim, ou se o status veio vazio/indefinido mas já tem placar de jogo passado, tratamos como Finalizado.
                        if raw_status in ["match finished", "ft", "full-time", "finished", "aet", "pen"]:
                            status = "Finalizado"
                        elif raw_status in ["ht", "halftime", "intervalo"]:
                            status = "Intervalo"
                        elif raw_status in ["live", "in play", "1h", "2h"]:
                            status = "Ao Vivo"
                        else:
                            # Se tem placar mas a API não mandou status claro, consideram-se jogos finalizados passados
                            status = "Finalizado"
                    else:
                        placar = "VS"
                        status = "Agendados"

                    jogos_formatados.append({
                        "id": i + 1,
                        "selecao": evento.get("strHomeTeam", "Brasil"),
                        "adversario": evento.get("strAwayTeam", "Adversário"),
                        "data": evento.get("dateEvent", "Em breve"),
                        "horario": evento.get("strTime", "A definir"),
                        "placar": placar,
                        "status": status,
                        "campeonato": evento.get("strLeague", "Partida Internacional"),
                    })
                return jogos_formatados

    except Exception as e:
        print(f"Erro ao consultar API externa: {e}")

    # Fallback caso ocorra algum problema na API externa
    return [{
        "id": 1,
        "selecao": "Brasil",
        "adversario": "Colômbia",
        "data": "2026-09-25",
        "horario": "16:00",
        "placar": "3 x 0",
        "status": "Finalizado",
        "campeonato": "Eliminatórias / Amistoso",
    }]
