from bs4 import BeautifulSoup
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
      "message": (
          "API Dinâmica do Live Goal conectada e puxando o calendário real da"
          " seleção!"
      ),
      "status": "online",
  }


@app.get("/api/selecao/jogos")
def get_jogos_selecao():
  jogos = []
  try:
    # URL pública de calendário esportivo (exemplo estruturado para varredura real)
    url = "https://www.espn.com.br/futebol/time/calendario/_/id/2094/selecao/brasil"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
      soup = BeautifulSoup(response.text, "html.parser")

      # Procura pelas linhas de tabela ou blocos de partidas no site da ESPN
      # O BeautifulSoup vai varrer a página real para capturar os confrontos
      linhas = soup.find_all("tr", class_="Table__TR")

      id_contador = 1
      for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) >= 3:
          try:
            # Extração dos dados reais direto da página da web
            data_jogo = colunas[0].get_text(strip=True)
            adversario = colunas[1].get_text(strip=True)
            placar_horario = colunas[2].get_text(strip=True)

            jogos.append({
                "id": id_contador,
                "selecao": "Brasil",
                "adversario": adversario,
                "data": data_jogo,
                "horario": "A definir",
                "placar": placar_horario,
                "status": (
                    "Ao Vivo" if "AO VIVO" in linha.get_text() else "Agendados"
                ),
                "campeonato": "Partida Oficial / Amistoso",
            })
            id_contador += 1
          except Exception:
            continue
  except Exception as e:
    print(f"Erro ao buscar dados reais: {e}")

  # Caso a raspagem sofra bloqueios temporários do servidor de terceiros,
  # mantemos uma estrutura de fallback para o site não ficar vazio.
  if not jogos:
    jogos = [{
        "id": 1,
        "selecao": "Brasil",
        "adversario": "Atualizando calendário oficial...",
        "data": "2026-10-01",
        "horario": "--:--",
        "placar": "- x -",
        "status": "Agendados",
        "campeonato": "Data FIFA",
    }]

  return jogos
