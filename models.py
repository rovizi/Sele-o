from database import Base
from sqlalchemy import Column, Integer, String


class PartidaModel(Base):
  __tablename__ = "partidas_selecao"

  id = Column(Integer, primary_key=True, index=True)
  selecao = Column(String, index=True)
  adversario = Column(String, index=True)
  data = Column(String)  # Formato YYYY-MM-DD
  horario = Column(String)  # Formato HH:MM
  placar = Column(String)
  status = Column(String)  # 'Finalizado', 'Ao Vivo', 'Agendados'
  campeonato = Column(String)