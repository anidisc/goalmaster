#library for my apifootball api
import os
import requests
import datetime
from rich.table import Table
from rich import print as rich_print


# Base URL e API key di API-FOOTBALL
API_URL = "https://v3.football.api-sports.io/"
API_KEY = os.environ.get("APIFOOTBALL_KEY")


class ApiFootball:
    def __init__(self):
        self.headers = {
            "x-rapidapi-host": "v3.football.api-sports.io",
            "x-rapidapi-key": API_KEY
        }
        self.YEAR = datetime.datetime.now().year  #set by default to current year

    def get_table_standings(self,league,year=datetime.datetime.now().year):
        url = f"{API_URL}/standings?league={league}&season={year}"
        params = {
            "league": league
        }
        response = requests.get(url, params=params, headers=self.headers)
        standings = response.json()

        table = Table(title=f"Classifica Dettagliata {year}")
        table.add_column("Pos", style="cyan")
        table.add_column("Squadra", style="magenta")
        table.add_column("PG", style="green")
        table.add_column("V", style="green")
        table.add_column("P", style="green")
        table.add_column("S", style="green")
        table.add_column("GF (C)", style="yellow")
        table.add_column("GS (C)", style="yellow")
        table.add_column("GF (F)", style="yellow")
        table.add_column("GS (F)", style="yellow")
        table.add_column("MGF (C)", style="yellow")
        table.add_column("MGF (F)", style="yellow")
        table.add_column("Andamento", style="bold")
        table.add_column("Punti", style="bold")

        for team in standings['response'][0]['league']['standings'][0]:
            position = str(team['rank'])
            team_name = team['team']['name']
            played_games = str(team['all']['played'])
            wins = str(team['all']['win'])
            draws = str(team['all']['draw'])
            losses = str(team['all']['lose'])
            
            goals_for_home = team['home']['goals']['for']
            goals_against_home = team['home']['goals']['against']
            goals_for_away = team['away']['goals']['for']
            goals_against_away = team['away']['goals']['against']
            
            # Calcolo media gol
            try:
                avg_goals_for_home = round(goals_for_home / team['home']['played'], 2)
                avg_goals_for_away = round(goals_for_away / team['away']['played'], 2)
            except ZeroDivisionError:
                avg_goals_for_home = 0
                avg_goals_for_away = 0  

        
            # Ultime 5 partite (simboli colorati)
            form = ""
            for result in team['form'].split():
                if result == 'W':
                    form += "[green]●[/green] "
                elif result == 'D':
                    form += "[white]●[/white] "
                elif result == 'L':
                    form += "[red]●[/red] "

            points = str(team['points'])

            table.add_row(
                position, team_name, played_games, wins, draws, losses,
                str(goals_for_home), str(goals_against_home),
                str(goals_for_away), str(goals_against_away),
                str(avg_goals_for_home), str(avg_goals_for_away),
                str(form), points
            )

        return table
        
m=ApiFootball().get_table_standings(135)
rich_print(m) #print(m)
