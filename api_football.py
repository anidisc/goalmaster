#library for my apifootball api
import os
import requests
from datetime import datetime, timedelta
import datetime as dt
from rich.table import Table
from rich import print as rich_print
from gm_data import Team, Match


# Base URL e API key di API-FOOTBALL
API_URL = "https://v3.football.api-sports.io/"
API_KEY = os.environ.get("APIFOOTBALL_KEY")


class ApiFootball:
    def __init__(self, year=datetime.now().year,timezone="Europe/Rome"):
        self.headers = {
            "x-rapidapi-host": "v3.football.api-sports.io",
            "x-rapidapi-key": API_KEY
        }
        self.YEAR = year
        self.timezone = timezone
    def get_status_apicalls(self):
        url = f"{API_URL}/status"
        response = requests.get(url, headers=self.headers)
        return 100 - int(response.json()['response']['requests']['current'])
    def get_standings(self,league):
        # get standings from api_football in a specific year from the api parameter and return a table with the data
        # static method (there is no need to create an instance of the class)
        url = f"{API_URL}/standings"
        params = {
            "league": league,
            "season": self.YEAR
        }
        response = requests.get(url, params=params, headers=self.headers)
        standings = response.json()
        self.rem = response.headers
        return standings
    def get_list_standings(self,league):
        
        """
        Get the standings of a league in a specific year from the api parameter and return a list of Team objects.
        
        Args:
            league (int): the league to get the standings for
        
        Returns:
            list: a list of Team objects representing the standings of the league
        """
        standings = self.get_standings(league)
        #memorize the table in a list of Team objects
        teams = []
        for t in standings['response'][0]['league']['standings'][0]:
            # add the team to the list
            teams.append(Team(t["team"]["id"],
                                t["team"]["name"],   
                                t["rank"],
                                t["points"],
                                t["all"]["played"],
                                t["team"]["logo"],
                                t["all"]["win"],
                                t["all"]["draw"],
                                t["all"]["lose"],
                                t["all"]["goals"]["for"],
                                t["all"]["goals"]["against"],
                                t["home"]["win"],
                                t["away"]["win"],
                                t["home"]["draw"],
                                t["away"]["draw"],
                                t["home"]["lose"],
                                t["away"]["lose"],
                                t["home"]["goals"]["for"],
                                t["away"]["goals"]["for"],
                                t["home"]["goals"]["against"],
                                t["away"]["goals"]["against"],
                                t["form"],
                                t["status"]
                                ))
        return teams   
    def get_table_standings(self,league):
        """
        Get the standings of a league in a specific year from the api parameter and return a rich.table.Table object.
        
        Args:
            league (int): the league to get the standings for
        
        Returns:
            rich.table.Table: a rich.table.Table object representing the standings of the league
        """
        standings = self.get_standings(league)
        table = Table(show_lines=False, show_header=True, header_style="bold",show_edge=False)
        table.add_column("POS", style="cyan")
        table.add_column("TEAM", style="magenta")
        table.add_column("P", style="bold")
        table.add_column("PG", style="green")
        table.add_column("W", style="green")
        table.add_column("D", style="green")
        table.add_column("L", style="green")
        table.add_column("GF(H)", style="yellow")
        table.add_column("GA(H)", style="yellow")
        table.add_column("GF(A)", style="yellow")
        table.add_column("GA(A)", style="yellow")
        table.add_column("MGF(H)", style="yellow")
        table.add_column("MGA(A)", style="yellow")
        table.add_column("Status", style="bold")
     

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
            form=""
            for result in list(str(team['form'])):
                if result == 'W':
                    form += "[green]●[/green]"
                elif result == 'D':
                    form += "[white]●[/white]"
                elif result == 'L':
                    form += "[red]●[/red]"

            points = str(team['points'])

            table.add_row(
                position, team_name, points, played_games, wins, draws, losses,
                str(goals_for_home), str(goals_against_home),
                str(goals_for_away), str(goals_against_away),
                str(avg_goals_for_home), str(avg_goals_for_away),form
            )
        #create a list of Team objects from the table
        #table = [Team(row) for row in table.rows]
        return table
    
    def get_fixtures(self,id_league,datefrom,dateto):
        url=f"{API_URL}/fixtures"
        params = {
            "league": id_league,
            "from": datefrom,
            "to": dateto,
            "season": self.YEAR,
            "timezone": self.timezone
        }
        response = requests.get(url, params=params, headers=self.headers)
        fixtures = response.json()
        return fixtures
    #get list of fixtures for live matches or speciafic league
    def get_fixture_live(self,leagues="all"):
        url=f"{API_URL}/fixtures"
        params = {
            "timezone": self.timezone,
            "live": leagues
        }
        response = requests.get(url, params=params, headers=self.headers)
        fixtures = response.json()
        return fixtures
    def get_list_fixtures(self,league,datefrom,dateto,live=False)->Match:
        #get list of fixtures in a specific league in obkect Match
        fixtures = self.get_fixtures(league,datefrom,dateto) if not live else self.get_fixture_live()
        list_fixtures = []
        for fixture in fixtures['response']:
            list_fixtures.append(Match(fixture['fixture']['id'],
                                       fixture['fixture']['date'],
                                       fixture['league']['round'],
                                       fixture['teams']['home']['name'],
                                       fixture['teams']['away']['name'],
                                       fixture['goals']['home'],
                                       fixture['goals']['away'],
                                       fixture['fixture']['status']['short'],
                                       fixture['fixture']['status']['elapsed'],
                                       fixture['fixture']['referee'],
                                       fixture['league']['country']))
            
        return list_fixtures
    def get_list_events_fixtures(self,id_fixture):
        url=f"{API_URL}/fixtures/events"
        params = {
            "fixture": id_fixture
        }
        response = requests.get(url, params=params, headers=self.headers)
        events = response.json()
        return events
    
#m=ApiFootball().get_table_standings(135)
#rich_print(ApiFootball().get_table_standings(135))
#rich_print("Status remaining calls :", ApiFootball().get_status())
#rich_print("standings italy 2023", ApiFootball(2023).get_table_standings(135))
# dfrom=dt.date.today()
# dto=dt.date.today()+timedelta(days=-30)
# rich_print(dfrom,dto)

# r=ApiFootball().get_list_fixtures(39,dto,dfrom)
# for i in range(len(r)):
#     rich_print(r[i])


