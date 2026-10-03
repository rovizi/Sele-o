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
                    
                    raw_status = evento.get("strStatus", "")
                    
                    # Trata o placar quando o jogo tem gols ou pontuação registrada
                    if score_home is not None and score_away is not None:
                        placar = f"{score_home} x {score_away}"
                        
                        # Mapeamento inteligente de status da partida
                        if raw_status == "Match Finished" or raw_status == "FT":
                            status = "Finalizado"
                        elif raw_status == "HT" or raw_status == "Halftime":
                            status = "Intervalo"
                        else:
                            status = "Ao Vivo"
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
