from datetime import datetime
from database import Base, engine, get_db
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import PartidaModel
from schemas import PartidaSchema
from sqlalchemy.orm import Session

# Cria as tabelas no banco de dados automaticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Live Goal Seleção API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def popular_dados_iniciais():
  db = next(get_db())
  total = db.query(PartidaModel).count()
  if total == 0:
    # Dados reais oficiais da Data FIFA (Brasil e Cabo Verde)
    dados_iniciais = [
        PartidaModel(
            selecao="Brasil",
            adversario="Austrália",
            data="2026-09-25",
            horario="07:00",
            placar="1 x 1",
            status="Finalizado",
            campeonato="Amistoso Internacional",
        ),
        PartidaModel(
            selecao="Cabo Verde",
            adversario="Mali",
            data="2026-09-25",
            horario="16:00",
            placar="Em breve",
            status="Agendados",
            campeonato="Eliminatórias da CAN",
        ),
        PartidaModel(
            selecao="Brasil",
            adversario="Austrália (Próximo Jogo)",
            data="2026-09-29",
            horario="07:00",
            placar="- x -",
            status="Agendados",
            campeonato="Amistoso Internacional",
        ),
        PartidaModel(
            selecao="Brasil",
            adversario="Índia",
            data="2026-10-03",
            horario="11:00",
            placar="- x -",
            status="Agendados",
            campeonato="Amistoso Internacional",
        ),
    ]
    db.add_all(dados_iniciais)
    db.commit()


@app.get("/")
def home():
  return {
      "message": (
          "API da Seleção do Live Goal com dados reais do Brasil e Cabo Verde"
          " online!"
      ),
      "status": "online",
  }


@app.get("/api/selecao/jogos", response_model=list[PartidaSchema])
def listar_jogos(db: Session = Depends(get_db)):
  partidas = db.query(PartidaModel).all()
  agora = datetime.now()

  # Lógica para mudar para 'Ao Vivo' automaticamente se faltar 10 minutos
  for p in partidas:
    data_hora_str = f"{p.data} {p.horario}"
    try:
      dt_jogo = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")
      diferenca_minutos = (dt_jogo - agora).total_seconds() / 60

      if -120 <= diferenca_minutos <= 10:
        if p.status != "Finalizado":
          p.status = "Ao Vivo"
    except ValueError:
      pass

  return partidas