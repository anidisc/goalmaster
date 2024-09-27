#library for my apifootball api
import os
import requests
from datetime import datetime, timedelta
import datetime as dt
from rich.table import Table
from rich import print as rich_print
from gm_data import Team, Match, Event, Stats, Formation, Player


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
        # Get the standings of the league
        standings = self.get_standings(league)

        # Create a rich.table.Table object
        table = Table(show_lines=False, show_header=True, header_style="bold",show_edge=False)

        # Add columns to the table
        table.add_column("POS", style="cyan") # Position
        table.add_column("TEAM", style="magenta") # Team name
        table.add_column("P", style="bold") # Points
        table.add_column("RO", style="green") # Rounds
        table.add_column("W", style="green") # Wins
        table.add_column("D", style="green") # Draws
        table.add_column("L", style="green") # Losses
        table.add_column("GF(H)", style="yellow") # Goals for at home
        table.add_column("GA(H)", style="yellow") # Goals against at home
        table.add_column("GF(A)", style="yellow") # Goals for away
        table.add_column("GA(A)", style="yellow") # Goals against away
        table.add_column("MGF(H)", style="yellow") # Average goals for at home
        table.add_column("MGA(A)", style="yellow") # Average goals against away
        table.add_column("Status", style="bold") # Status of the team

        # Loop through the standings and add rows to the table
        for team in standings['response'][0]['league']['standings'][0]:
            # Get the team's position, name, points, played games, wins, draws, losses, goals for and against at home and away
            position = str(team['rank'])
            team_name = team['team']['name']
            points = str(team['points'])
            played_games = str(team['all']['played'])
            wins = str(team['all']['win'])
            draws = str(team['all']['draw'])
            losses = str(team['all']['lose'])
            goals_for_home = team['home']['goals']['for']
            goals_against_home = team['home']['goals']['against']
            goals_for_away = team['away']['goals']['for']
            goals_against_away = team['away']['goals']['against']

            # Calculate average goals for and against at home and away
            try:
                avg_goals_for_home = round(goals_for_home / team['home']['played'], 2)
                avg_goals_for_away = round(goals_for_away / team['away']['played'], 2)
            except ZeroDivisionError:
                avg_goals_for_home = 0
                avg_goals_for_away = 0  

            # Get the team's form (last 5 matches)
            form=""
            for result in list(str(team['form'])):
                if result == 'W':
                    form += "[green]●[/green]"
                elif result == 'D':
                    form += "[white]●[/white]"
                elif result == 'L':
                    form += "[red]●[/red]"

            # Add the row to the table
            table.add_row(
                position, team_name, points, played_games, wins, draws, losses,
                str(goals_for_home), str(goals_against_home),
                str(goals_for_away), str(goals_against_away),
                str(avg_goals_for_home), str(avg_goals_for_away),
                form
            )

        # Return the table
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
                if event.event == "Goal" or event.event == "Normal Goal":
                    event.event = f"[green]G O A L[/green]"
                else:
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
    
    def get_list_statistics_match(self, id_fixture: int) -> list[Stats]:
        """
        Get the statistics of a match from the API and return a list of Stats objects.

        Args:
            id_fixture (int): The id of the fixture to get the statistics for

        Returns:
            List[Stats]: A list of Stats objects
        """
        statistics = self.get_statistics_match(id_fixture)
        list_teams_stats = []
        for team in statistics['response']:
            list_teams_stats.append(Stats(
                team_name=team['team']['name'],
                shots_on_goal=team['statistics'][0]['value'],
                shots_off_goal=team['statistics'][1]['value'],
                shots_insidebox=team['statistics'][2]['value'],
                shots_outsidebox=team['statistics'][3]['value'],
                total_shots=team['statistics'][4]['value'],
                blocked_shots=team['statistics'][5]['value'],
                fouls=team['statistics'][6]['value'],
                corners_kicks=team['statistics'][7]['value'],
                offsides=team['statistics'][8]['value'],
                ball_possession=team['statistics'][9]['value'],
                yellow_card=team['statistics'][10]['value'],
                red_card=team['statistics'][11]['value'],
                goalkeepers_saves=team['statistics'][12]['value'],
                total_passes=team['statistics'][13]['value'],
                passes_accurate=team['statistics'][14]['value'],
                passes_percentage=team['statistics'][15]['value']
            ))
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
    
    def get_formation_teams(self, id_match) -> Formation:
        
        """
        Get the formation of a team from the API and return a Formation object.

        Args:
            id_match (int): The id of the match to get the formation for

        Returns:
            Formation: A Formation object
        """
        url = f"{API_URL}/fixtures/lineups"
        params = {
            "fixture": id_match

        }
        response = requests.get(url, headers=self.headers, params=params)
        t1=response.json()['response'][0]
        t2=response.json()['response'][1]
        t1formation=[]
        t2formation=[]
        for i in range(11):
            t1formation.append(Player(t1['startXI'][i]['player']['name'],
                                      t1['startXI'][i]['player']['grid'],
                                      t1['startXI'][i]['player']['pos'],
                                      t1['startXI'][i]['player']['number']))
            t2formation.append(Player(t2['startXI'][i]['player']['name'],
                                      t2['startXI'][i]['player']['grid'],
                                      t2['startXI'][i]['player']['pos'],
                                      t2['startXI'][i]['player']['number']))
        #add substitutions
        for i in t1['substitutes']:
            t1formation.append(Player(i['player']['name'],
                                      i['player']['grid'],
                                      i['player']['pos'],
                                      i['player']['number']))
        for i in t2['substitutes']:
            t2formation.append(Player(i['player']['name'],
                                      i['player']['grid'],
                                      i['player']['pos'],
                                      i['player']['number']))
        
        return Formation(t1['team']['name'],t1['formation'],t1formation,t1['coach']['name']), Formation(t2['team']['name'],t2['formation'],t2formation,t2['coach']['name'])


#m=ApiFootball().get_table_standings(135)
# testo=str(rich_print(ApiFootball().get_table_standings(135)))                                                                                                                                                                                                                                                                                                                                            
# print(type(testo))
#rich_print("Status remaining calls :", ApiFootball().get_status())
#rich_print("standings italy 2023", ApiFootball(2023).get_table_standings(135))
# dfrom=dt.date.today()
# dto=dt.date.today()+timedelta(days=-30)
# rich_print(dfrom,dto)

# r=ApiFootball().get_list_fixtures(135,dto,dfrom)
# for i in range(len(r)):
#     rich_print(f"{r[i]}, {r[i].id}")

#rich_print(ApiFootball().print_table_standings(1223632))
f1,f2=ApiFootball().get_formation_teams(1223649)
rich_print(f1.team_name,f1.formation,f1.coach)
for i in f1.player:
    rich_print(i.name,i.role,i.position,i.number)