#library for my apifootball api
import os
import requests
from datetime import datetime, timedelta
import datetime as dt
from rich.table import Table
from rich import print as rich_print
from gm_data import Team, Match, Event, Stats


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
        table.add_column("RO", style="green")
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
        #sort list by date
        list_fixtures.sort(key=lambda x: x.date) 
        #and then sort by country   
        list_fixtures.sort(key=lambda x: x.country)
            
        return list_fixtures
    def get_list_events_fixtures(self,id_fixture):
        url=f"{API_URL}/fixtures/events"
        params = {
            "fixture": id_fixture
        }
        response = requests.get(url, params=params, headers=self.headers)
        events = response.json()
        events_list_flow = []
        for event in events['response']:
            extratime = event["time"]["extra"] if event["time"]["extra"] != None else 0
            events_list_flow.append(Event(event["team"]["name"],
                                          event["detail"],
                                          event["time"]["elapsed"]+extratime,
                                          event["player"]["name"],
                                          event["assist"]["name"]if event["assist"] != None else "",
                                          event["comments"]if event["comments"] != None else ""))
        return events_list_flow
    def get_table_event_flow(self,id_fixture):
        events_list_flow = self.get_list_events_fixtures(id_fixture)
        table = Table(show_lines=False, show_header=True, header_style="bold",show_edge=False)
        table.add_column("Time", style="cyan")
        table.add_column("Event", style="magenta", justify="center")
        table.add_column("Team", style="yellow")
        table.add_column("Player", style="green")
        table.add_column("Assist", style="blue")
        table.add_column("Comment", style="white")
        for event in events_list_flow:
            #color the event according to type
            if event.event == "Goal" or event.event == "Own Goal" or event.event == "Penalty" or event.event == "Normal Goal":
                event.event = f"[green]{event.event}[/green]"
            elif event.event == "Yellow Card":
                event.event = f"[yellow]{event.event}[/yellow]"
            elif event.event == "Red Card":
                event.event = f"[red]{event.event}[/red]"
            elif event.event == "Substitution 1" or event.event == "Substitution 2" or event.event == "Substitution 3" or event.event == "Substitution 4" or event.event == "Substitution 5":
                event.event = f"[blue]{event.event}[/blue]"
            table.add_row(str(event.minute)+"'",
                          event.event,
                          event.team,
                          event.player,
                          event.assist,
                          event.comment)
        return table
    def get_statistics_match(self,id_fixture):
        url=f"{API_URL}/fixtures/statistics"
        params = {
            "fixture": id_fixture
        }
        response = requests.get(url, params=params, headers=self.headers)
        statistics = response.json()
        return statistics
    
    def get_list_statistics_match(self,id_fixture):
        statistics = self.get_statistics_match(id_fixture)
        list_teams_stats = []
        for team in statistics['response']:
            list_teams_stats.append(Stats(team['team']['name'],
                                          team['statistics'][0]['value'],
                                          team['statistics'][1]['value'],
                                          team['statistics'][2]['value'],
                                          team['statistics'][3]['value'],
                                          team['statistics'][4]['value'],
                                          team['statistics'][5]['value'],
                                          team['statistics'][6]['value'],
                                          team['statistics'][7]['value'],
                                          team['statistics'][8]['value'],
                                          team['statistics'][9]['value'],
                                          team['statistics'][10]['value'],
                                          team['statistics'][11]['value'],
                                          team['statistics'][12]['value'],
                                          team['statistics'][13]['value'],
                                          team['statistics'][14]['value'],
                                          team['statistics'][15]['value']))
        return list_teams_stats
    
    def print_table_standings(self,league):
        s=self.get_list_statistics_match(league)
        table = Table(show_lines=False, show_header=True, header_style="bold",show_edge=False)
        table.add_column("Stats", style="cyan")
        table.add_column(s[0].team_name.upper(), style="cyan", justify="center")
        table.add_column(s[1].team_name.upper(), style="magenta", justify="center")
        table.add_row("ball possession", str(s[0].ball_possession)+"%", str(s[1].ball_possession)+"%")
        table.add_row("shoots on goals", str(s[0].shots_on_goal), str(s[1].shots_on_goal))
        table.add_row("shoots off goals", str(s[0].shots_off_goal), str(s[1].shots_off_goal))
        table.add_row("shots on target", str(s[0].shots_insidebox), str(s[1].shots_insidebox))
        table.add_row("shots off target", str(s[0].shots_outsidebox), str(s[1].shots_outsidebox))
        table.add_row("total shots", str(s[0].total_shots), str(s[1].total_shots))
        table.add_row("blocked shots", str(s[0].blocked_shots), str(s[1].blocked_shots))
        table.add_row("offsides", str(s[0].offsides), str(s[1].offsides))
        table.add_row("corners", str(s[0].corners_kicks), str(s[1].corners_kicks))
        table.add_row("fouls", str(s[0].fouls), str(s[1].fouls))
        table.add_row("yellow cards", str(s[0].yellow_card), str(s[1].yellow_card))
        table.add_row("red cards", str(s[0].red_card), str(s[1].red_card))
        table.add_row("saves", str(s[0].goalkeepers_saves), str(s[1].goalkeepers_saves))
        table.add_row("total passes", str(s[0].total_passes), str(s[1].total_passes))
        table.add_row("accurate passes", str(s[0].passes_accurate), str(s[1].passes_accurate))
        table.add_row("percentage passes", str(s[0].passes_percentage)+"%", str(s[1].passes_percentage)+"%")


        return table

#m=ApiFootball().get_table_standings(135)
#rich_print(ApiFootball().get_table_standings(135))
#rich_print("Status remaining calls :", ApiFootball().get_status())
#rich_print("standings italy 2023", ApiFootball(2023).get_table_standings(135))
# dfrom=dt.date.today()
# dto=dt.date.today()+timedelta(days=-30)
# rich_print(dfrom,dto)

# r=ApiFootball().get_list_fixtures(135,dto,dfrom)
# for i in range(len(r)):
#     rich_print(f"{r[i]}, {r[i].id}")

#rich_print(ApiFootball().print_table_standings(1223632))