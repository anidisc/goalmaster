#library for my apifootball api
import json
import os
import requests
from datetime import datetime, timedelta
import datetime as dt
from rich.table import Table
from rich import print as rich_print
from gm_data import League, Team, Match, Event, Stats, Formation, Player, TopPlayer, TeamStats,PlayerInjury
import datetime as dt


# Base URL e API key di API-FOOTBALL
API_URL = "https://api-football-v1.p.rapidapi.com/v3" #rapidapi
API_KEY = os.environ.get("APIFOOTBALL_KEY")
PREDICTION_FILE_DB = "predictions.json"
STANDINGS_FILE_DB = "standings.json"
TEAM_STATISTICS_FILE_DB="team_statistics.json"
INJURYPLAYER_FILE_DB="player_injury.json"


class ApiFootball:
    def __init__(self, year=datetime.now().year,timezone="Europe/Rome"):
        self.headers = {
            "x-rapidapi-key": API_KEY,
	        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
        }
        self.YEAR = 2024 if (year==2025) else year #TODO change to the current year ad start of the season
        self.timezone = timezone
        self.remains_calls = 100

    def get_standings(self,league,update=False):
        # get standings from api_football in a specific year from the api parameter and return a table with the data
        # static method (there is no need to create an instance of the class)
        url = f"{API_URL}/standings"
        params = {
            "league": league,
            "season": self.YEAR
        }
        current_date = str(dt.date.today())
        strleague = str(league)
        try:
            with open(STANDINGS_FILE_DB, "r") as f:
                standing_to_disk = json.load(f)
        except FileNotFoundError: #create file and structure data inside
            response = requests.get(url, params=params, headers=self.headers)
            standings = response.json()['response'][0]['league']['standings']
            data={league:{
                "standing":{
                    "date":current_date,
                    "standings":standings}
                }}
            with open(STANDINGS_FILE_DB, "w") as f:
                json.dump(data, f)
            return standings
        #check if the headers from the file json are still valid
        if (strleague in standing_to_disk) and (update == False):
            if standing_to_disk[strleague]["standing"]["date"] == current_date:
                return standing_to_disk[strleague]["standing"]["standings"]
        #otherwise get the standings from api_football
        response = requests.get(url, params=params, headers=self.headers)
        standings = response.json()['response'][0]['league']['standings']
        #update API_CALLS
        self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))

        datanew={"standing":{"date":current_date,"standings":standings}}

        standing_to_disk[league] = datanew
        #save the standigs in the file append the new standings
        with open(STANDINGS_FILE_DB, "w") as f:
            json.dump(standing_to_disk, f)
        return standings
        #self.rem = response.headers

    def get_list_standings(self,league,update=False):

        """
        Get the standings of a league in a specific year from the api parameter and return a list of Team objects.

        Args:
            league (int): the league to get the standings for

        Returns:
            list: a list of Team objects representing the standings of the league
        """
        standings = self.get_standings(league,update)
        #memorize the table in a list of list of Team objects
        nl=len(standings)
        teams = [[] for _ in range(nl)]

        for n in range(nl):
            for t in standings[n]:
            # add the team to the list
                teams[n].append(Team(t["team"]["id"],
                                    t["team"]["name"],
                                    t["rank"],
                                    t["points"],
                                    t["all"]["played"],
                                    t["team"]["logo"],
                                    t['home']['played'],
                                    t['away']['played'],
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
    def get_table_standings(self,standings):
        """
        Get the standings of a league in a specific year from the api parameter and return a rich.table.Table object.

        Args:
            league (int): the league to get the standings for

        Returns:
            rich.table.Table: a rich.table.Table object representing the standings of the league
        """
        # Get the standings of the league
        #standings = self.get_standings(league)['response'][0]['league']['standings'][group]

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
        table.add_column("GF", style="yellow") # Goals for
        table.add_column("GA", style="red") # Goals against
        table.add_column("GF(H)", style="yellow") # Goals for at home
        table.add_column("GA(H)", style="yellow") # Goals against at home
        table.add_column("GF(A)", style="yellow") # Goals for away
        table.add_column("GA(A)", style="yellow") # Goals against away
        table.add_column("MGF(H)", style="yellow") # Average goals for at home
        table.add_column("MGA(A)", style="yellow") # Average goals against away
        table.add_column("Status", style="bold") # Status of the team

        # Loop through the standings and add rows to the table
        for team in standings:
            # Get the team's position, name, points, played games, wins, draws, losses, goals for and against at home and away
            position = str(team.position)
            team_name = team.name
            points = str(team.points)
            played_games = str(team.matches)
            wins = str(team.wins)
            draws = str(team.draws)
            losses = str(team.losses)
            goals_for=str(team.goals_for)
            goals_against=str(team.goals_against)
            goals_for_home = team.goals_for_home
            goals_against_home = team.goals_against_home
            goals_for_away = team.goals_for_away
            goals_against_away = team.goals_against_away

            # Calculate average goals for and against at home and away
            try:
                avg_goals_for_home = round(goals_for_home / team.home_played, 2)
                avg_goals_for_away = round(goals_for_away / team.away_played, 2)
            except ZeroDivisionError:
                avg_goals_for_home = 0
                avg_goals_for_away = 0

            # Get the team's form (last 5 matches)
            form=""
            for result in list(str(team.last_5_matches)):
                if result == 'W':
                    form += "[green]●[/green]"
                elif result == 'D':
                    form += "[white]●[/white]"
                elif result == 'L':
                    form += "[red]●[/red]"

            # Add the row to the table
            table.add_row(
                position, team_name, points, played_games, wins, draws, losses, goals_for, goals_against,
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

        #update API_CALLS
        self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))

        fixtures = response.json()
        return fixtures
    #get list of fixtures for live matches or speciafic league
    def get_fixture_live(self,leagues="all"):
        url=f"https://api-football-v1.p.rapidapi.com/v3/fixtures"
        params = {
            "timezone": self.timezone,
            "live": leagues
        }
        response = requests.get(url, params=params, headers=self.headers)
        #update API_CALLS
        self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))

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
                                       fixture['league']['country'],
                                       fixture['teams']['home']['id'],
                                       fixture['teams']['away']['id'],
                                       id_league=league))
        #sort list by date
        list_fixtures.sort(key=lambda x: x.date)
        #and then sort by country
        list_fixtures.sort(key=lambda x: x.country)
        #check if the predictions are available in the file json
        try:
            with open(PREDICTION_FILE_DB, "r") as f:
                predictions = json.load(f)
                for match in list_fixtures:
                    if str(match.id) in predictions:
                        match.prediction = True
        except FileNotFoundError:
            pass  # file doesn't exist and do nothing

        return list_fixtures
    def get_list_events_fixtures(self,id_fixture):
        url=f"{API_URL}/fixtures/events"
        params = {
            "fixture": id_fixture
        }
        response = requests.get(url, params=params, headers=self.headers)
        #update API_CALLS
        self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))

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
                    event.event = f"[green]●GOAL●[/green]"
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
        #update API_CALLS
        self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))
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
            
        #update API_CALLS
        self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))

        return Formation(t1['team']['name'],t1['formation'],t1formation,t1['coach']['name']), Formation(t2['team']['name'],t2['formation'],t2formation,t2['coach']['name'])

    def print_table_formations(self, id_match) -> None:
        f1,f2=self.get_formation_teams(id_match)
        #print table for team 1 and 2 with line between starting XI and substitutes and coach
        table = Table(show_lines=False, show_header=True, header_style="bold",show_edge=False)
        table.add_column(f"{f1.team_name}", style="cyan", justify="left")
        table.add_column(f"{f2.team_name}", style="blue", justify="right")
        c=0
        for i,j in zip(f1.player,f2.player):
            table.add_row(f"{i.role} {' '+str(i.number) if i.number<10 else i.number} {i.name}",f"{j.name} {str(j.number)+' ' if j.number<10 else j.number} {j.role}")
            c+=1
            if c==11: #add line
                table.add_row("-- Subst --","-- Subst --",style="bold green")


        table.add_row("", "", style="bold blue")
        table.add_row(f1.coach,f2.coach, style="bold magenta")
        return table
    #get list of all leagues
    def get_list_leagues(self) -> list[League]:
        url = f"{API_URL}/leagues"
        response = requests.get(url, headers=self.headers)
        #update API_CALLS
        self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))

        l=[]
        for league in response.json()['response']:
            l.append(League(league['league']['id'],
                            league['league']['name'],
                            league['league']['type'],
                            league['country']['name']))
        #dsort listy by country
        l.sort(key=lambda x: x.country)
        return l

    #get response from api_football of prediction function
    def get_prediction(self, id_match):
        url = f"{API_URL}/predictions"
        params = {
            "fixture": id_match
        }
        response = requests.get(url, headers=self.headers, params=params)
        #update API_CALLS
        self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))

        return response.json()['response']

    #get top scores from api_football
    # def get_top_scores(self,id_league,assists=False) -> list[TopPlayer]:
    #     url = f"{API_URL}/players/topscorers" if not assists else f"{API_URL}/players/topassists"
    #     params = {
    #         "league": id_league,
    #         "season": self.YEAR
    #     }
    #     response = requests.get(url, headers=self.headers, params=params)
    #     res_json = response.json()['response']
    #     #update API_CALLS
    #     self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))

    #     top_players = []
    #     for player in res_json:
    #         top_players.append(TopPlayer(player['player']['name'],
    #                                      player['statistics'][0]['games']['position'],
    #                                      "",
    #                                      player['statistics'][0]['games']['number'],
    #                                      player['statistics'][0]['team']['name'],
    #                                      player['statistics'][0]['goals']['total'],
    #                                      player['statistics'][0]['goals']['assists'],
    #                                      player['statistics'][0]['cards']['yellow'],
    #                                      player['statistics'][0]['cards']['red'],
    #                                      player['player']['nationality'],
    #                                      player['player']['age'],
    #                                      player['statistics'][0]['penalty']['scored'],
    #                                      player['statistics'][0]['penalty']['missed']))

    #     return top_players
    
    def get_top_scores(self, id_league) -> list[TopPlayer]:
        file_path = "topscore_players.json"
        today = datetime.today().date()

        # Se il file esiste, carica i dati
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    cache = json.load(f)
                except json.JSONDecodeError:
                    cache = {}
        else:
            cache = {}

        # Controlla se i dati sono aggiornati a meno di 4 giorni
        if (str(id_league) in cache and datetime.strptime(cache[str(id_league)]["date"], "%Y-%m-%d").date() >= today - timedelta(days=4)):
            res_json = cache[str(id_league)]["response"]
        else:
            url = f"{API_URL}/players/topscorers"
            params = {"league": id_league, "season": self.YEAR}
            response = requests.get(url, headers=self.headers, params=params)
            res_json = response.json()['response']
            
            # Aggiorna API_CALLS
            self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining', 0))
            
            # Salva i dati nel file
            cache[str(id_league)] = {"date": today.strftime("%Y-%m-%d"), "response": res_json}
            with open(file_path, "w") as f:
                json.dump(cache, f, indent=4)

        # Continua con la creazione della lista dei TopPlayer
        top_players = []
        for player in res_json:
            top_players.append(TopPlayer(
                player['player']['name'],
                player['statistics'][0]['games']['position'],
                "",
                player['statistics'][0]['games']['number'],
                player['statistics'][0]['team']['name'],
                player['statistics'][0]['goals']['total'],
                player['statistics'][0]['goals']['assists'],
                player['statistics'][0]['cards']['yellow'],
                player['statistics'][0]['cards']['red'],
                player['player']['nationality'],
                player['player']['age'],
                player['statistics'][0]['penalty']['scored'],
                player['statistics'][0]['penalty']['missed']
            ))

        return top_players
    #def a function to get table of top scorers from api_football

    def get_top_assists(self, id_league) -> list[TopPlayer]:
        file_path = "topassist_players.json"
        today = datetime.today().date()

        # Se il file esiste, carica i dati
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    cache = json.load(f)
                except json.JSONDecodeError:
                    cache = {}
        else:
            cache = {}

        # Controlla se i dati sono aggiornati a meno di 4 giorni
        if (str(id_league) in cache and datetime.strptime(cache[str(id_league)]["date"], "%Y-%m-%d").date() >= today - timedelta(days=4)):
            res_json = cache[str(id_league)]["response"]
        else:
            url = f"{API_URL}/players/topassists"
            params = {"league": id_league, "season": self.YEAR}
            response = requests.get(url, headers=self.headers, params=params)
            res_json = response.json()['response']
            
            # Aggiorna API_CALLS
            self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining', 0))
            
            # Salva i dati nel file
            cache[str(id_league)] = {"date": today.strftime("%Y-%m-%d"), "response": res_json}
            with open(file_path, "w") as f:
                json.dump(cache, f, indent=4)

        # Continua con la creazione della lista dei TopPlayer
        top_players = []
        for player in res_json:
            top_players.append(TopPlayer(
                player['player']['name'],
                player['statistics'][0]['games']['position'],
                "",
                player['statistics'][0]['games']['number'],
                player['statistics'][0]['team']['name'],
                player['statistics'][0]['goals']['total'],
                player['statistics'][0]['goals']['assists'],
                player['statistics'][0]['cards']['yellow'],
                player['statistics'][0]['cards']['red'],
                player['player']['nationality'],
                player['player']['age'],
                player['statistics'][0]['penalty']['scored'],
                player['statistics'][0]['penalty']['missed']
            ))

        return top_players
    
    def table_top_scores(self,id_league,assists=False) -> None:

        top_players = self.get_top_scores(id_league) if not assists else self.get_top_assists(id_league)

        table = Table(show_lines=False, show_header=True, header_style="bold",show_edge=False)

        table.add_column("Player", style="white", justify="left")
        table.add_column("Position", style="blue", justify="left")
        table.add_column("Team", style="cyan", justify="left")
        table.add_column("Goals", style="blue", justify="left")
        table.add_column("Ass.", style="blue", justify="left")
        table.add_column("Pen.S-M", style="cyan", justify="left")
        table.add_column("YC", style="yellow", justify="left")
        table.add_column("RC", style="red", justify="left")
        table.add_column("Nationality", style="blue", justify="left")
        table.add_column("Age", style="blue", justify="left")
        for player in top_players:
            table.add_row(player.name,
                          player.position,
                          player.team,
                          str(player.goals),
                          str(player.assists),
                          str(player.penalty_scored)+"-"+str(player.penalty_missed),
                          str(player.yellow_cards),
                          str(player.red_cards),
                          player.nationality,
                          str(player.age)
                          )

        return table

    #def a function that get team statistic from api_football
    def get_team_statistics(self,id_team,id_league):
        url = f"{API_URL}/teams/statistics"
        params = {
            "team": id_team,
            "league": id_league,
            "season": self.YEAR
        }
        #save response in json file if not exist
        id_team=str(id_team)+"-#"+str(id_league)
        data={}
        try:
            with open(TEAM_STATISTICS_FILE_DB, "r") as f:
                team_statistics_to_disk = json.load(f)
        except FileNotFoundError: #create file and structure data inside
            with open(TEAM_STATISTICS_FILE_DB, "w") as f:
                response = requests.get(url, headers=self.headers, params=params)
                #update API_CALLS
                self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))
                data[id_team]={"data":{"date":datetime.now().strftime("%Y-%m-%d"),"statistics":response.json()['response']}}
                json.dump(data, f,indent=4)
            return response.json()['response']
        #check if the headers from the file json are still valid
        #otherwise get the standings from api_football
        #check if id_team is in the file json
        if id_team in team_statistics_to_disk:
            date_limit = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
            if team_statistics_to_disk[id_team]["data"]["date"] >= date_limit: #== datetime.now().strftime("%Y-%m-%d"):
                return team_statistics_to_disk[id_team]["data"]["statistics"]
        else:
            response = requests.get(url, headers=self.headers, params=params)
            #update API_CALLS
            self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))
            #data={"id_team":id_team,"data":{"date":datetime.now().strftime("%Y-%m-%d"),"statistics":response.json()['response']}}
            data[id_team]={"data":{"date":datetime.now().strftime("%Y-%m-%d"),"statistics":response.json()['response']}}
            team_statistics_to_disk.update(data)
            with open(TEAM_STATISTICS_FILE_DB, "w") as f:
                json.dump(team_statistics_to_disk, f,indent=4)
            return response.json()['response']
        
        
    #def a fun that print a table of team statistic from api_football to compare two teams
    def print_table_compareteams(self,team1, team2):
        
        from rich import box
        from rich.text import Text

        # Campi da escludere
        excluded_fields = [
            "team_id", "team_logo", "league_id", "league_flag", "league_logo"#,"lineups","form"
        ]


        def add_rows_recursive(table, prefix, data1, data2):
            """Aggiunge righe alla tabella per ogni campo trovato nei dizionari, escludendo quelli indicati."""
            for key in (set(data1.keys()).union(data2.keys())):
                if f"{prefix}{key}" in excluded_fields:
                    continue  # Salta i campi esclusi

                val1 = data1.get(key, "-")
                val2 = data2.get(key, "-")

                if key == "form":
                    # Visualizza il campo `form` con pallini colorati
                    val1 = format_form(val1)
                    val2 = format_form(val2)
                elif key == "lineups":
                    # Visualizza `lineups` in maniera leggibile
                    val1 = format_lineups(val1)
                    val2 = format_lineups(val2)
                elif isinstance(val1, dict) or isinstance(val2, dict):
                    # Se il valore è un dizionario, continua la ricorsione
                    sub_data1 = val1 if isinstance(val1, dict) else {}
                    sub_data2 = val2 if isinstance(val2, dict) else {}
                    #exclude to add row if value is None
                    if sub_data1=={} and sub_data2=={}:
                        continue
                    add_rows_recursive(table, f"{prefix}{key}.", sub_data1, sub_data2)
                    continue
                else:
                    val1 = str(val1 or "-")
                    val2 = str(val2 or "-")
                if val1 == "-" and val2 == "-":
                    continue
                table.add_row(f"{prefix}{key}", val1, val2)

        def format_form(form_string):
            """Formatta il campo `form` con pallini colorati."""
            if not form_string or not isinstance(form_string, str):
                return "N/A"
            text = Text()
            #make the char arrow right in the table
            ch_green="🟩"
            ch_yellow="🟨"
            ch_red="🟥"
            for char in form_string:
                if char == "W":
                    text.append(ch_green, style="green")
                elif char == "D":
                    text.append(ch_yellow, style="yellow")
                elif char == "L":
                    text.append(ch_red, style="red")
                else:
                    text.append(f"{char} ", style="dim")
            return text

        def format_lineups(lineups):
            """Formatta il campo `lineups` in maniera leggibile."""
            if not lineups or not isinstance(lineups, list):
                return "N/A"
            return "\n".join(f"Formation: {item['formation']} - Played: {item['played']}" for item in lineups)

        # Creazione della tabella
        table = Table(title="Team Comparison", show_lines=False, box=box.ROUNDED)
        table.add_column("Attribute", justify="left", style="bold")
        table.add_column(team1.team_name or "Team 1", justify="center", style="cyan")
        table.add_column(team2.team_name or "Team 2", justify="center", style="magenta")

        # Aggiunta delle righe
        add_rows_recursive(table, "", team1.__dict__, team2.__dict__)
        # Stampa la tabella
        return table
    
    #def a funnction that extract the injuries player from api_football
    def get_players_injuries(self,id_league,date):
        url = f"{API_URL}/injuries"
        params = {"league": id_league,
                  "season": self.YEAR,
                  "date": date}
        response = requests.get(url, headers=self.headers, params=params)
        #update API_CALLS
        self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))
        return response.json()['response']
    def get_list_injuries_by_date(self,id_league,date) -> dict:
        #check if file of injuries exist
        data={}
        id_league=str(id_league)
        if os.path.isfile(INJURYPLAYER_FILE_DB):
            with open(INJURYPLAYER_FILE_DB, "r") as f:
                injuries_to_disk=json.load(f)
            if id_league in injuries_to_disk:
                if injuries_to_disk[id_league]["date"]>=date:
                    response=injuries_to_disk[id_league]["injuries"]
                else:
                    response=self.get_players_injuries(id_league,date)
                    injuries_to_disk[id_league]={"date":date,"injuries":response}
                    with open(INJURYPLAYER_FILE_DB,"w") as f:
                        json.dump(injuries_to_disk,f,indent=4)
            else:
                response=self.get_players_injuries(id_league,date)
                injuries_to_disk[id_league]={"date":date,"injuries":response}
                with open(INJURYPLAYER_FILE_DB,"w") as f:
                    json.dump(injuries_to_disk,f,indent=4)
        else:
            with open(INJURYPLAYER_FILE_DB, "w") as f:
                response=self.get_players_injuries(id_league,date)
                #save response in json file if not exist
                data[id_league]={"date":date,"injuries":response}
                json.dump(data,f,indent=4)
        
        list_injuries = {}

        for res in response:
            id = str(res['fixture']['id'])  # ID del fixture (può ripetersi)
            idplayer = str(res['player']['id'])  # ID univoco del giocatore
            playername = res['player']['name']
            teamname = res['team']['name']
            reason = res['player']['reason']

            # Se l'ID non è presente, lo creiamo con un nuovo dizionario contenente idplayer
            if id not in list_injuries:
                list_injuries[id] = {}

            # Aggiungiamo il giocatore al dizionario dell'ID senza sovrascrivere gli altri
            list_injuries[id][idplayer] = {
                "playername": playername,
                "teamname": teamname,
                "reason": reason
            }


        return list_injuries
    

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
# f1,f2=ApiFootball().get_formation_teams(1223649)
# rich_print(f1.team_name,f1.formation,f1.coach)
# for i in f1.player:
#     rich_print(i.name,i.role,i.position,i.number)
#rich_print(ApiFootball().print_table_formations(1223649))

# l=ApiFootball().get_list_leagues()
# for i in l:
#     rich_print(f"{i.id} {i.name} {i.country} {i.type}")

# s=ApiFootball().get_list_standings(135)
# rich_print(ApiFootball().get_table_standings(s[0]))
#rich_print(ApiFootball().get_prediction(1234713))
# topplayers=(ApiFootball().get_top_scores(135))
# for i in topplayers:
#     rich_print(i.name,i.position,i.team,i.number,i.goals,i.assists,i.nationality,i.age)
#rich_print(ApiFootball().table_top_scores(135))
# response1=ApiFootball().get_team_statistics(492,135)
# response2=ApiFootball().get_team_statistics(490,135)
# ts1,ts2=TeamStats(),TeamStats()
# ts1.Charge_Data(response1)
# ts2.Charge_Data(response2)
# rich_print(ApiFootball().print_table_compareteams(ts1,ts2))
# #rich_print(ts1.get_table_stats())
# #rich_print(ts1.get_table_stats())

# x=ApiFootball().get_list_injuries_by_date(135,"2025-02-01")
# inj=(json.dumps(x["1223820"],indent=4))
# rich_print(inj)
# #print al player injuries
# for i in x:
#     rich_print(i.name,i.reason,i.team,i.idfixture)