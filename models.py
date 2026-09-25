from database import Base
from sqlalchemy import Column, Integer, String


class PartidaModel(Base):
  __tablename__ = "partidas"

  id = Column(Integer, primary_key=True, index=True)
  selecao = Column(String, index=True)
  adversario = Column(String, index=True)
  data = Column(String)
  horario = Column(String)
  placar = Column(String)
  status = Column(String)
  campeonato = Column(String)
