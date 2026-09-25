from pydantic import BaseModel


class PartidaSchema(BaseModel):
  id: int
  selecao: str
  adversario: str
  data: str
  horario: str
  placar: str
  status: str
  campeonato: str

  class Config:
    from_attributes = True