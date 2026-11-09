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
    # Data e hora oficial do jogo (Exemplo: Brasil x Japão em 14/11/2026 às 07:15)
    data_jogo_str = "2026-11-14 07:15:00"
    data_jogo = datetime.strptime(data_jogo_str, "%Y-%m-%d %H:%M:%S")
    
    agora = datetime.now()
    diferenca = data_jogo - agora
    
    # Comparações de dias
    hoje_data = agora.date()
    data_do_jogo_date = data_jogo.date()
    amanha_data = hoje_data + timedelta(days=1)
    
    horario_formatado = data_jogo.strftime("%H:%M")

    # 1. Lógica inteligente de texto de data ("Hoje", "Amanhã" ou a data completa)
    if data_do_jogo_date == hoje_data:
        data_exibida = f"Hoje às {horario_formatado}"
    elif data_do_jogo_date == amanha_data:
        data_exibida = f"Amanhã às {horario_formatado}"
    else:
        data_exibida = "Sábado, 14/11/2026 às 07:15"

    # 2. Lógica de Status e Transição de Abas (10 minutos antes vai para Ao Vivo)
    # Se faltar 10 minutos ou menos (e a partida não tiver acabado), muda para pré-ao vivo / andamento
    status_partida = "PRE" # Padrão: Agendado
    
    # Se já passou da hora ou faltam menos de 10 minutos (timedelta de 10 minutos = minutes=10)
    if timedelta(0) <= diferenca <= timedelta(minutes=10):
        status_partida = "LIVE" # Muda para a aba Ao Vivo 10 min antes
    elif diferenca < timedelta(0):
        # Aqui a API da ESPN vai injetar o status real se estiver rolando ou encerrado
        # Exemplo simulado: "LIVE" se estiver em andamento, "FT" se encerrado
        status_partida = "LIVE" 

    jogos = [
        {
            "id": 1,
            "home_team": "Brasil",
            "away_team": "Japão",
            "home_flag": "https://i.postimg.cc/URL_DA_BANDEIRA_DO_BRASIL", # Mantenha o link que você já usa
            "away_flag": "https://i.postimg.cc/URL_DA_BANDEIRA_DO_JAPAO", # Mantenha o link que você já usa
            "status": status_partida,  # Alterna automaticamente entre PRE e LIVE conforme o relógio
            "date": data_exibida,      # Retorna "Hoje", "Amanhã" ou a data normal
            "timestamp": "2026-11-14T07:15:00",
            "stadium": "Estádio Nacional de Singapura",
            "sub_info": "Jogo amistoso",
            "competition": "Amistoso Internacional"
        }
    ]

    return jogos
