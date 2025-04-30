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
TOPSCORE_PLAYERS_FILE_DB="topscore_players.json"
TOPASS_PLAYERS_FILE_DB="topassist_players.json"

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
    def get_top_scores(self, id_league) -> list[TopPlayer]:
        file_path = TOPSCORE_PLAYERS_FILE_DB
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
        file_path = TOPASS_PLAYERS_FILE_DB
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

        table.add_column("Player", style="white")
        table.add_column("Position", style="blue")
        table.add_column("Team", style="cyan")
        table.add_column("Goals", style="blue")
        table.add_column("Ass.", style="blue")
        table.add_column("Pen.S-M", style="cyan")
        table.add_column("YC", style="yellow")
        table.add_column("RC", style="red")
        table.add_column("Nationality", style="blue")
        table.add_column("Age", style="blue")
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
        team_statistics_to_disk = {}
        
        # Gestione più robusta della lettura del file
        try:
            with open(TEAM_STATISTICS_FILE_DB, "r", encoding="utf-8") as f:
                try:
                    team_statistics_to_disk = json.load(f)
                    #print(f"Statistics loaded for {len(team_statistics_to_disk)} teams")
                except json.JSONDecodeError:
                    # print(f"Error decoding {TEAM_STATISTICS_FILE_DB}, creating new file")
                    team_statistics_to_disk = {}
        except FileNotFoundError: #create file and structure data inside
            # print(f"File {TEAM_STATISTICS_FILE_DB} not found, creating new file")
            # Non facciamo nulla qui, il file verrà creato sotto
            pass
        
        # Se il file era vuoto o non esisteva, facciamo una chiamata API e creiamo il file
        if not team_statistics_to_disk:
            try:
                response = requests.get(url, headers=self.headers, params=params)
                #update API_CALLS
                self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))
                
                # Verifica che la risposta contenga i dati attesi
                if 'response' in response.json():
                    data[id_team]={"data":{"date":datetime.now().strftime("%Y-%m-%d"),"statistics":response.json()['response']}}
                    with open(TEAM_STATISTICS_FILE_DB, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    return response.json()['response']
                else:
                    # print(f"API response does not contain expected data: {response.json()}")
                    return None
            except Exception as e:
                # print(f"Error fetching team statistics: {str(e)}")
                return None
        
        # Se abbiamo caricato i dati dal file, verifichiamo se contengono i dati della squadra richiesta
        if id_team in team_statistics_to_disk:
            try:
                date_limit = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
                if team_statistics_to_disk[id_team]["data"]["date"] >= date_limit: #== datetime.now().strftime("%Y-%m-%d"):
                    return team_statistics_to_disk[id_team]["data"]["statistics"]
            except KeyError as e:
                # print(f"Data structure error for team {id_team}: {str(e)}")
                # Continua con una nuova richiesta API
                pass
        
        # Se arriviamo qui, i dati non ci sono o sono obsoleti, facciamo una nuova richiesta
        try:
            response = requests.get(url, headers=self.headers, params=params)
            #update API_CALLS
            self.remains_calls = int(response.headers.get('x-ratelimit-requests-remaining'))
            
            # Verifica che la risposta contenga i dati attesi
            if 'response' in response.json():
                data[id_team]={"data":{"date":datetime.now().strftime("%Y-%m-%d"),"statistics":response.json()['response']}}
                team_statistics_to_disk.update(data)
                with open(TEAM_STATISTICS_FILE_DB, "w", encoding="utf-8") as f:
                    json.dump(team_statistics_to_disk, f, indent=4, ensure_ascii=False)
                return response.json()['response']
            else:
                # print(f"API response does not contain expected data: {response.json()}")
                return None
        except Exception as e:
            # print(f"Error fetching or saving team statistics: {str(e)}")
            return None
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
        
        # Utilizziamo la data corrente del sistema come riferimento per gli aggiornamenti
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Calcoliamo la data limite per l'aggiornamento (4 giorni fa)
        date_limit = (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
        
        if os.path.isfile(INJURYPLAYER_FILE_DB):
            with open(INJURYPLAYER_FILE_DB, "r") as f:
                injuries_to_disk=json.load(f)
            if id_league in injuries_to_disk:
                # Verifichiamo se i dati sono vecchi (più di 4 giorni)
                stored_date = injuries_to_disk[id_league]["date"]
                if stored_date >= date_limit:
                    # Dati ancora validi, li utilizziamo
                    response=injuries_to_disk[id_league]["injuries"]
                else:
                    # Dati troppo vecchi, aggiorniamo con la data corrente
                    response=self.get_players_injuries(id_league,date)
                    injuries_to_disk[id_league]={"date":current_date,"injuries":response}
                    with open(INJURYPLAYER_FILE_DB,"w") as f:
                        json.dump(injuries_to_disk,f,indent=4)
            else:
                response=self.get_players_injuries(id_league,date)
                injuries_to_disk[id_league]={"date":current_date,"injuries":response}
                with open(INJURYPLAYER_FILE_DB,"w") as f:
                    json.dump(injuries_to_disk,f,indent=4)
        else:
            with open(INJURYPLAYER_FILE_DB, "w") as f:
                response=self.get_players_injuries(id_league,date)
                #save response in json file if not exist
                data[id_league]={"date":current_date,"injuries":response}
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
    
    def generate_injury_table(self, id_league, date, id_fixture) -> Table:
        """
        Genera una tabella Rich Text con gli infortuni per un specifico fixture
        Args:
            id_league: ID della lega
            date: Data di riferimento
            id_fixture: ID del fixture da visualizzare
        Returns:
            Oggetto Table di Rich
        """
        # Ottieni la lista degli infortuni
        injuries_data = self.get_list_injuries_by_date(id_league, date)
        
        # Converti l'ID in stringa per compatibilità
        id_fixture = str(id_fixture)
        
        # Controlla se ci sono infortuni per questo fixture
        if id_fixture not in injuries_data:
            table = Table(title=f"Nessun infortunio trovato - Fixture {id_fixture}")
            table.add_column("Info")
            table.add_row("Nessun giocatore infortunato per questo match")
            return table
        
        # Estrai i dati degli infortuni
        fixture_data = injuries_data[id_fixture]
        
        # Raggruppa giocatori per squadra
        teams = {}
        for player in fixture_data.values():
            team_name = player['teamname']
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append(player)
        
        # Crea la tabella
        table = Table(title=f"Infortuni Fixture {id_fixture}")
        table.add_column("Squadra", style="cyan", no_wrap=True)
        table.add_column("Giocatore", style="magenta")
        table.add_column("Motivazione", style="yellow")
        
        # Popola la tabella
        for team, players in teams.items():
            # Aggiungi una riga separatrice tra le squadre
            if len(table.rows) > 0:
                table.add_section()
            
            for i, player in enumerate(players):
                table.add_row(
                    team if i == 0 else "",  # Mostra il nome squadra solo una volta
                    player['playername'],
                    player['reason']
                )
        
        return table


    #def a function that print a table of team statistic from api_football to compare two teams
    def print_table_compareteams(self, team1, team2):
        """
        Creates a comprehensive comparison of team statistics.
        
        Args:
            team1: TeamStats object for the first team
            team2: TeamStats object for the second team
            
        Returns:
            Rich renderable with detailed comparative statistics
        """
        from rich import box
        from rich.table import Table
        from rich.panel import Panel
        from rich.layout import Layout
        from rich.console import Group
        from rich.columns import Columns
        from rich.align import Align
        from rich.text import Text
        
        # Handle potential missing data gracefully
        team1_name = team1.team_name or "Team 1"
        team2_name = team2.team_name or "Team 2"
        
        try:
            # Create a layout for better organization
            layout = Layout()
            layout.split_column(
                #Layout(name="header"),
                Layout(name="main_stats"),
                Layout(name="detailed_stats")
            )
            
            # Header with team names and league info
            # header_text = Text(f"[bold cyan]{team1_name}[/bold cyan] vs [bold magenta]{team2_name}[/bold magenta]")
            # header_text.append("\n")
            # header_text.append(f"[yellow]{team1.league_name or 'Unknown'}[/yellow] ({team1.league_country or 'Unknown'}) | Season: [green]{team1.league_season or 'Unknown'}[/green]")
            
            # layout["header"].update(Align.center(header_text))
            
            # Main statistics section
            main_stats_tables = []
            
            # Form information 
            form_table = Table(title="Recent Form", box=box.ROUNDED)
            form_table.add_column("Team", style="bold")
            form_table.add_column("Form", no_wrap=True)
            
            form1 = self._format_form_string(team1.form) if team1.form else "No data"
            form2 = self._format_form_string(team2.form) if team2.form else "No data"
            
            form_table.add_row(team1_name, form1)
            form_table.add_row(team2_name, form2)
            
            main_stats_tables.append(form_table)
            
            # Fixtures statistics table
            if isinstance(team1.fixtures, dict) and isinstance(team2.fixtures, dict):
                fixtures_table = Table(title="Fixtures Statistics", box=box.ROUNDED)
                fixtures_table.add_column("Statistic", style="bold")
                fixtures_table.add_column(team1_name, style="cyan")
                fixtures_table.add_column(team2_name, style="magenta")
                
                # Home/Away/Total Played
                if "played" in team1.fixtures and "played" in team2.fixtures:
                    fixtures_table.add_row(
                        "Games Played (Home)",
                        str(team1.fixtures["played"].get("home", 0)),
                        str(team2.fixtures["played"].get("home", 0))
                    )
                    fixtures_table.add_row(
                        "Games Played (Away)",
                        str(team1.fixtures["played"].get("away", 0)),
                        str(team2.fixtures["played"].get("away", 0))
                    )
                    fixtures_table.add_row(
                        "Games Played (Total)",
                        str(team1.fixtures["played"].get("total", 0)),
                        str(team2.fixtures["played"].get("total", 0))
                    )
                
                # Wins statistics
                if "wins" in team1.fixtures and "wins" in team2.fixtures:
                    fixtures_table.add_row(
                        "Wins (Home)",
                        str(team1.fixtures["wins"].get("home", 0)),
                        str(team2.fixtures["wins"].get("home", 0))
                    )
                    fixtures_table.add_row(
                        "Wins (Away)",
                        str(team1.fixtures["wins"].get("away", 0)),
                        str(team2.fixtures["wins"].get("away", 0))
                    )
                    fixtures_table.add_row(
                        "Wins (Total)",
                        str(team1.fixtures["wins"].get("total", 0)),
                        str(team2.fixtures["wins"].get("total", 0))
                    )
                
                # Draws statistics
                if "draws" in team1.fixtures and "draws" in team2.fixtures:
                    fixtures_table.add_row(
                        "Draws (Home)",
                        str(team1.fixtures["draws"].get("home", 0)),
                        str(team2.fixtures["draws"].get("home", 0))
                    )
                    fixtures_table.add_row(
                        "Draws (Away)",
                        str(team1.fixtures["draws"].get("away", 0)),
                        str(team2.fixtures["draws"].get("away", 0))
                    )
                    fixtures_table.add_row(
                        "Draws (Total)",
                        str(team1.fixtures["draws"].get("total", 0)),
                        str(team2.fixtures["draws"].get("total", 0))
                    )
                
                # Losses statistics
                if "loses" in team1.fixtures and "loses" in team2.fixtures:
                    fixtures_table.add_row(
                        "Losses (Home)",
                        str(team1.fixtures["loses"].get("home", 0)),
                        str(team2.fixtures["loses"].get("home", 0))
                    )
                    fixtures_table.add_row(
                        "Losses (Away)",
                        str(team1.fixtures["loses"].get("away", 0)),
                        str(team2.fixtures["loses"].get("away", 0))
                    )
                    fixtures_table.add_row(
                        "Losses (Total)",
                        str(team1.fixtures["loses"].get("total", 0)),
                        str(team2.fixtures["loses"].get("total", 0))
                    )
                
                main_stats_tables.append(fixtures_table)
            
            # Goals statistics
            if isinstance(team1.goals, dict) and isinstance(team2.goals, dict):
                goals_table = Table(title="Goals Statistics", box=box.ROUNDED)
                goals_table.add_column("Statistic", style="bold")
                goals_table.add_column(team1_name, style="cyan")
                goals_table.add_column(team2_name, style="magenta")
                
                # Goals For
                if "for" in team1.goals and "for" in team2.goals:
                    if "total" in team1.goals["for"] and "total" in team2.goals["for"]:
                        goals_table.add_row(
                            "Goals Scored (Home)",
                            str(team1.goals["for"]["total"].get("home", 0)),
                            str(team2.goals["for"]["total"].get("home", 0))
                        )
                        goals_table.add_row(
                            "Goals Scored (Away)",
                            str(team1.goals["for"]["total"].get("away", 0)),
                            str(team2.goals["for"]["total"].get("away", 0))
                        )
                        goals_table.add_row(
                            "Goals Scored (Total)",
                            str(team1.goals["for"]["total"].get("total", 0)),
                            str(team2.goals["for"]["total"].get("total", 0))
                        )
                    
                    if "average" in team1.goals["for"] and "average" in team2.goals["for"]:
                        goals_table.add_row(
                            "Avg Goals Scored (Home)",
                            str(team1.goals["for"]["average"].get("home", 0)),
                            str(team2.goals["for"]["average"].get("home", 0))
                        )
                        goals_table.add_row(
                            "Avg Goals Scored (Away)",
                            str(team1.goals["for"]["average"].get("away", 0)),
                            str(team2.goals["for"]["average"].get("away", 0))
                        )
                        goals_table.add_row(
                            "Avg Goals Scored (Total)",
                            str(team1.goals["for"]["average"].get("total", 0)),
                            str(team2.goals["for"]["average"].get("total", 0))
                        )
                
                # Goals Against
                if "against" in team1.goals and "against" in team2.goals:
                    if "total" in team1.goals["against"] and "total" in team2.goals["against"]:
                        goals_table.add_row(
                            "Goals Conceded (Home)",
                            str(team1.goals["against"]["total"].get("home", 0)),
                            str(team2.goals["against"]["total"].get("home", 0))
                        )
                        goals_table.add_row(
                            "Goals Conceded (Away)",
                            str(team1.goals["against"]["total"].get("away", 0)),
                            str(team2.goals["against"]["total"].get("away", 0))
                        )
                        goals_table.add_row(
                            "Goals Conceded (Total)",
                            str(team1.goals["against"]["total"].get("total", 0)),
                            str(team2.goals["against"]["total"].get("total", 0))
                        )
                    
                    if "average" in team1.goals["against"] and "average" in team2.goals["against"]:
                        goals_table.add_row(
                            "Avg Goals Conceded (Home)",
                            str(team1.goals["against"]["average"].get("home", 0)),
                            str(team2.goals["against"]["average"].get("home", 0))
                        )
                        goals_table.add_row(
                            "Avg Goals Conceded (Away)",
                            str(team1.goals["against"]["average"].get("away", 0)),
                            str(team2.goals["against"]["average"].get("away", 0))
                        )
                        goals_table.add_row(
                            "Avg Goals Conceded (Total)",
                            str(team1.goals["against"]["average"].get("total", 0)),
                            str(team2.goals["against"]["average"].get("total", 0))
                        )
                
                main_stats_tables.append(goals_table)
            
            # Clean sheets and Failed to score
            additional_stats_table = Table(title="Additional Statistics", box=box.ROUNDED)
            additional_stats_table.add_column("Statistic", style="bold")
            additional_stats_table.add_column(team1_name, style="cyan")
            additional_stats_table.add_column(team2_name, style="magenta")
            
            # Clean sheets
            if isinstance(team1.clean_sheet, dict) and isinstance(team2.clean_sheet, dict):
                additional_stats_table.add_row(
                    "Clean Sheets (Home)",
                    str(team1.clean_sheet.get("home", 0)),
                    str(team2.clean_sheet.get("home", 0))
                )
                additional_stats_table.add_row(
                    "Clean Sheets (Away)",
                    str(team1.clean_sheet.get("away", 0)),
                    str(team2.clean_sheet.get("away", 0))
                )
                additional_stats_table.add_row(
                    "Clean Sheets (Total)",
                    str(team1.clean_sheet.get("total", 0)),
                    str(team2.clean_sheet.get("total", 0))
                )
            
            # Failed to score
            if isinstance(team1.failed_to_score, dict) and isinstance(team2.failed_to_score, dict):
                additional_stats_table.add_row(
                    "Failed to Score (Home)",
                    str(team1.failed_to_score.get("home", 0)),
                    str(team2.failed_to_score.get("home", 0))
                )
                additional_stats_table.add_row(
                    "Failed to Score (Away)",
                    str(team1.failed_to_score.get("away", 0)),
                    str(team2.failed_to_score.get("away", 0))
                )
                additional_stats_table.add_row(
                    "Failed to Score (Total)",
                    str(team1.failed_to_score.get("total", 0)),
                    str(team2.failed_to_score.get("total", 0))
                )
            
            main_stats_tables.append(additional_stats_table)
            
            # Penalty statistics
            if isinstance(team1.penalty, dict) and isinstance(team2.penalty, dict):
                penalty_table = Table(title="Penalty Statistics", box=box.ROUNDED)
                penalty_table.add_column("Statistic", style="bold")
                penalty_table.add_column(team1_name, style="cyan")
                penalty_table.add_column(team2_name, style="magenta")
                
                if "scored" in team1.penalty and "scored" in team2.penalty:
                    penalty_table.add_row(
                        "Penalties Scored",
                        str(team1.penalty["scored"].get("total", 0)),
                        str(team2.penalty["scored"].get("total", 0))
                    )
                    
                if "missed" in team1.penalty and "missed" in team2.penalty:
                    penalty_table.add_row(
                        "Penalties Missed",
                        str(team1.penalty["missed"].get("total", 0)),
                        str(team2.penalty["missed"].get("total", 0))
                    )
                    
                if "total" in team1.penalty and "total" in team2.penalty:
                    penalty_table.add_row(
                        "Total Penalties",
                        str(team1.penalty.get("total", 0)),
                        str(team2.penalty.get("total", 0))
                    )
                
                main_stats_tables.append(penalty_table)
            
            # Cards statistics
            if isinstance(team1.cards, dict) and isinstance(team2.cards, dict):
                cards_table = Table(title="Cards Statistics", box=box.ROUNDED)
                cards_table.add_column("Statistic", style="bold")
                cards_table.add_column(team1_name, style="cyan")
                cards_table.add_column(team2_name, style="magenta")
                
                # Yellow cards
                if "yellow" in team1.cards and "yellow" in team2.cards:
                    # cards_table.add_row(
                    #     "Yellow Cards (Total)",
                    #     str(team1.cards["yellow"].get("total", 0)),
                    #     str(team2.cards["yellow"].get("total", 0))
                    # )
                    
                    # Add time ranges for yellow cards if available
                    time_ranges = ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "91-105", "106-120"]
                    for time_range in time_ranges:
                        if time_range in team1.cards["yellow"] and time_range in team2.cards["yellow"]:
                            cards_table.add_row(
                                f"Yellow Cards ({time_range} min)",
                                str(team1.cards["yellow"].get(time_range, 0)["total"]),
                                str(team2.cards["yellow"].get(time_range, 0)["total"])
                            )
                
                # Red cards
                if "red" in team1.cards and "red" in team2.cards:
                    # cards_table.add_row(
                    #     "Red Cards (Total)",
                    #     str(team1.cards["red"].get("total", 0)),
                    #     str(team2.cards["red"].get("total", 0))
                    # )
                    
                    # Add time ranges for red cards if available
                    for time_range in time_ranges:
                        if time_range in team1.cards["red"] and time_range in team2.cards["red"]:
                            cards_table.add_row(
                                f"Red Cards ({time_range} min)",
                                str(team1.cards["red"].get(time_range, 0)["total"]),
                                str(team2.cards["red"].get(time_range, 0)["total"])
                            )
                
                main_stats_tables.append(cards_table)
            
            # Most used lineups
            if team1.lineups and team2.lineups and isinstance(team1.lineups, list) and isinstance(team2.lineups, list):
                lineup_table = Table(title="Formation Information", box=box.ROUNDED)
                lineup_table.add_column("Team", style="bold")
                lineup_table.add_column("Formation", style="bold")
                lineup_table.add_column("Games Played", style="bold")
                
                # Add up to 3 most used formations for each team
                max_formations = min(len(team1.lineups), len(team2.lineups), 3)
                
                # Team 1 formations
                for i in range(max_formations):
                    if i < len(team1.lineups) and isinstance(team1.lineups[i], dict):
                        lineup_table.add_row(
                            team1_name if i == 0 else "",
                            team1.lineups[i].get("formation", "Unknown"),
                            str(team1.lineups[i].get("played", 0))
                        )
                
                # Add a separator row
                lineup_table.add_row("", "", "")
                
                # Team 2 formations
                for i in range(max_formations):
                    if i < len(team2.lineups) and isinstance(team2.lineups[i], dict):
                        lineup_table.add_row(
                            team2_name if i == 0 else "",
                            team2.lineups[i].get("formation", "Unknown"),
                            str(team2.lineups[i].get("played", 0))
                        )
                
                main_stats_tables.append(lineup_table)
            
            # Arrange tables in columns
            layout["main_stats"].update(Columns(main_stats_tables))
            
            # Create detailed stats section for goal minute distribution
            detailed_stats_tables = []
            
            if isinstance(team1.goals, dict) and isinstance(team2.goals, dict):
                # Goal distributions by minute
                if "for" in team1.goals and "for" in team2.goals:
                    if "minute" in team1.goals["for"] and "minute" in team2.goals["for"]:
                        goals_minute_table = Table(title="Goals Scored by Minute", box=box.ROUNDED)
                        goals_minute_table.add_column("Time Range", style="bold")
                        goals_minute_table.add_column(f"{team1_name} (Scored)", style="cyan")
                        goals_minute_table.add_column(f"{team2_name} (Scored)", style="magenta")
                        
                        time_ranges = ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "91-105", "106-120"]
                        for time_range in time_ranges:
                            if time_range in team1.goals["for"]["minute"] and time_range in team2.goals["for"]["minute"]:
                                goals_minute_table.add_row(
                                    time_range,
                                    f"{team1.goals['for']['minute'][time_range].get('total', 0)} ({team1.goals['for']['minute'][time_range].get('percentage', '0%')})",
                                    f"{team2.goals['for']['minute'][time_range].get('total', 0)} ({team2.goals['for']['minute'][time_range].get('percentage', '0%')})"
                                )
                        
                        detailed_stats_tables.append(goals_minute_table)
                
                # Goals conceded by minute
                if "against" in team1.goals and "against" in team2.goals:
                    if "minute" in team1.goals["against"] and "minute" in team2.goals["against"]:
                        conceded_minute_table = Table(title="Goals Conceded by Minute", box=box.ROUNDED)
                        conceded_minute_table.add_column("Time Range", style="bold")
                        conceded_minute_table.add_column(f"{team1_name} (Conceded)", style="cyan")
                        conceded_minute_table.add_column(f"{team2_name} (Conceded)", style="magenta")
                        
                        time_ranges = ["0-15", "16-30", "31-45", "46-60", "61-75", "76-90", "91-105", "106-120"]
                        for time_range in time_ranges:
                            if time_range in team1.goals["against"]["minute"] and time_range in team2.goals["against"]["minute"]:
                                conceded_minute_table.add_row(
                                    time_range,
                                    f"{team1.goals['against']['minute'][time_range].get('total', 0)} ({team1.goals['against']['minute'][time_range].get('percentage', '0%')})",
                                    f"{team2.goals['against']['minute'][time_range].get('total', 0)} ({team2.goals['against']['minute'][time_range].get('percentage', '0%')})"
                                )
                        
                        detailed_stats_tables.append(conceded_minute_table)
            
            # Biggest stats
            if hasattr(team1, 'biggest') and hasattr(team2, 'biggest'):
                if isinstance(team1.biggest, dict) and isinstance(team2.biggest, dict):
                    biggest_table = Table(title="Record Statistics", box=box.ROUNDED)
                    biggest_table.add_column("Statistic", style="bold")
                    biggest_table.add_column(team1_name, style="cyan")
                    biggest_table.add_column(team2_name, style="magenta")
                    
                    # Streak information
                    if "streak" in team1.biggest and "streak" in team2.biggest:
                        biggest_table.add_row(
                            "Longest Win Streak",
                            str(team1.biggest["streak"].get("wins", 0)),
                            str(team2.biggest["streak"].get("wins", 0))
                        )
                        biggest_table.add_row(
                            "Longest Draw Streak",
                            str(team1.biggest["streak"].get("draws", 0)),
                            str(team2.biggest["streak"].get("draws", 0))
                        )
                        biggest_table.add_row(
                            "Longest Loss Streak",
                            str(team1.biggest["streak"].get("loses", 0)),
                            str(team2.biggest["streak"].get("loses", 0))
                        )
                    
                    # Biggest wins
                    if "wins" in team1.biggest and "wins" in team2.biggest:
                        biggest_table.add_row(
                            "Biggest Home Win",
                            str(team1.biggest["wins"].get("home", "N/A")),
                            str(team2.biggest["wins"].get("home", "N/A"))
                        )
                        biggest_table.add_row(
                            "Biggest Away Win",
                            str(team1.biggest["wins"].get("away", "N/A")),
                            str(team2.biggest["wins"].get("away", "N/A"))
                        )
                    
                    # Biggest losses
                    if "loses" in team1.biggest and "loses" in team2.biggest:
                        biggest_table.add_row(
                            "Biggest Home Loss",
                            str(team1.biggest["loses"].get("home", "N/A")),
                            str(team2.biggest["loses"].get("home", "N/A"))
                        )
                        biggest_table.add_row(
                            "Biggest Away Loss",
                            str(team1.biggest["loses"].get("away", "N/A")),
                            str(team2.biggest["loses"].get("away", "N/A"))
                        )
                    
                    # Biggest goals
                    if "goals" in team1.biggest and "goals" in team2.biggest:
                        if "for" in team1.biggest["goals"] and "for" in team2.biggest["goals"]:
                            biggest_table.add_row(
                                "Most Goals Scored (Home)",
                                str(team1.biggest["goals"]["for"].get("home", 0)),
                                str(team2.biggest["goals"]["for"].get("home", 0))
                            )
                            biggest_table.add_row(
                                "Most Goals Scored (Away)",
                                str(team1.biggest["goals"]["for"].get("away", 0)),
                                str(team2.biggest["goals"]["for"].get("away", 0))
                            )
                        
                        if "against" in team1.biggest["goals"] and "against" in team2.biggest["goals"]:
                            biggest_table.add_row(
                                "Most Goals Conceded (Home)",
                                str(team1.biggest["goals"]["against"].get("home", 0)),
                                str(team2.biggest["goals"]["against"].get("home", 0))
                            )
                            biggest_table.add_row(
                                "Most Goals Conceded (Away)",
                                str(team1.biggest["goals"]["against"].get("away", 0)),
                                str(team2.biggest["goals"]["against"].get("away", 0))
                            )
                    
                    detailed_stats_tables.append(biggest_table)
            
            # Add goals over/under stats if available
            if isinstance(team1.goals, dict) and isinstance(team2.goals, dict):
                if "for" in team1.goals and "for" in team2.goals:
                    if "under_over" in team1.goals["for"] and "under_over" in team2.goals["for"]:
                        goals_ou_table = Table(title="Goals Scored Over/Under", box=box.ROUNDED)
                        goals_ou_table.add_column("Over/Under", style="bold")
                        goals_ou_table.add_column(f"{team1_name} Over", style="cyan")
                        goals_ou_table.add_column(f"{team1_name} Under", style="cyan")
                        goals_ou_table.add_column(f"{team2_name} Over", style="magenta")
                        goals_ou_table.add_column(f"{team2_name} Under", style="magenta")
                        
                        thresholds = ["0.5", "1.5", "2.5", "3.5", "4.5"]
                        for threshold in thresholds:
                            if threshold in team1.goals["for"]["under_over"] and threshold in team2.goals["for"]["under_over"]:
                                goals_ou_table.add_row(
                                    threshold,
                                    str(team1.goals["for"]["under_over"][threshold].get("over", 0)),
                                    str(team1.goals["for"]["under_over"][threshold].get("under", 0)),
                                    str(team2.goals["for"]["under_over"][threshold].get("over", 0)),
                                    str(team2.goals["for"]["under_over"][threshold].get("under", 0))
                                )
                        
                        detailed_stats_tables.append(goals_ou_table)
            
            # Arrange detailed tables in columns
            layout["detailed_stats"].update(Columns(detailed_stats_tables))

            # Alla fine della funzione, prima di return layout:
            from rich.console import Console
            from io import StringIO

            console = Console(file=open("stats_output.txt", "w"), width=250,height=150)
            console.print(layout)

            memfile = StringIO()
            memconsole = Console(file=memfile,width=100,height=200)
            memconsole.print(layout)

            return memfile.getvalue()
        
            
        except Exception as e:
            # Fallback to a simple table if there's an error
            error_table = Table(title="Team Comparison")
            error_table.add_column("Team")
            error_table.add_column("Info")
            error_table.add_row(team1_name, "Basic stats not available")
            error_table.add_row(team2_name, "Basic stats not available")
            return error_table

        
    
    def _format_form_string(self, form_string):
        """Format the form string to visual indicators"""
        if not form_string or not isinstance(form_string, str):
            return "No data"
            
        result = ""
        for char in form_string:
            if char == "W":
                result += "🟢"
            elif char == "D":
                result += "🟡"
            elif char == "L":
                result += "🔴"
            else:
                result += char
                
        return result

#print statisti between twi teams
# import gm_data as gm
# r1 = ApiFootball().get_team_statistics(517,135)
# r2 = ApiFootball().get_team_statistics(489,135)
# g1,g2 = gm.TeamStats(),gm.TeamStats()
# g1.Charge_Data(r1)
# g2.Charge_Data(r2)
# rich_print(ApiFootball().print_table_compareteams(g1,g2)# Modifichiamo il codice di test per verificare i dati

# import gm_data as gm
# from rich.console import Console
# from rich import print as rich_print

# console = Console(width=150)  # Impostiamo una larghezza maggiore

# r1 = ApiFootball().get_team_statistics(517, 135)
# r2 = ApiFootball().get_team_statistics(489, 135)
# g1, g2 = gm.TeamStats(), gm.TeamStats()
# g1.Charge_Data(r1)
# g2.Charge_Data(r2)

# # Stampiamo la tabella con una console più ampia
# result = ApiFootball().print_table_compareteams(g1, g2)
# console.print(result)

# def print_table_compareteams(self, team1, team2):
#     # Resto del codice invariato
    
#     # Alla fine della funzione, prima di return layout:
#     from rich.console import Console
#     console = Console(file=open("stats_output.txt", "w"), width=200)
#     console.print(layout)
    
#     return layout
