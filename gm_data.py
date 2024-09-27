#data structure of the app
from datetime import datetime
class Team:
    def __init__(self, id, name, position, points, matches, logo,
                 wins, draws, losses, goals_for, goals_against,
                 win_home, win_away, home_draw, away_draw, lose_home, lose_away,
                 goals_for_home, goals_for_away,
                 goals_against_home, goals_against_away,
                 last_5_matches,status_form):
        """
        Class for structure data of a soccer team.

        Args:
            id (int): unique identifier of the team
            name (str): name of the team
            position (int): position of the team in the league
            points (int): number of points earned by the team
            matches (int): number of matches played
            wins (int): number of wins
            draws (int): number of draws
            losses (int): number of losses
            goals_for (int): number of goals scored
            goals_against (int): number of goals against
            win_home (int): number of wins at home
            win_away (int): number of wins away
            draw (int): number of draws
            lose_home (int): number of losses at home
            lose_away (int): number of losses away
            goals_home (int): number of goals scored at home
            goals_away (int): number of goals scored away
            goals_for_home (int): number of goals scored at home
            goals_for_away (int): number of goals scored away
            last_5_matches (list): list of the last 5 matches played
            status_form (str): status of the form (win, lose, draw)
        """
        self.id = id
        self.name = name
        self.position = position
        self.points = points
        self.matches = matches
        self.wins = wins
        self.draws = draws
        self.losses = losses
        self.goals_for = goals_for
        self.goals_against = goals_against
        self.last_5_matches = last_5_matches
        self.status_form = status_form
        self.win_home = win_home
        self.win_away = win_away
        self.home_draw = home_draw
        self.away_draw = away_draw
        self.lose_home = lose_home
        self.lose_away = lose_away
        self.goals_against_home = goals_against_home
        self.goals_against_away = goals_against_away
        self.goals_for_home = goals_for_home
        self.goals_for_away = goals_for_away
        self.logo = logo
    
    #function to calculate medius stats
    def medius_goals_for(self):
        #medius between goasl_for and goals_against in the number of matches
        """
        Calculate the average goals scored by the team in all matches.
        
        Returns:
            float: The average goals scored by the team.
        """
        try:
            return (self.goals_for) / self.matches
        except ZeroDivisionError:
            return 0
    def medius_goals_against(self):
        #medius between goals for in the matches and goals against in the number of matches
        try:
            return (self.goals_against) / self.matches
        except ZeroDivisionError:
            return 0
    def goal_difference(self):
        """
        Calculate the difference between the goals scored by the team and the goals scored against the team.
        
        Returns:
            int: The difference between the goals scored by the team and the goals scored against the team.
        """
        return self.goals_for - self.goals_against
    #medius between goals for home
    def medius_goals_for_home(self):
        try:
            return (self.goals_for_home) / self.matches
        except ZeroDivisionError:
            return 0
    #medius between goals for away
    def medius_goals_for_away(self):
        try:
            return (self.goals_for_away) / self.matches
        except ZeroDivisionError:
            return 0
    

class Match:
    def __init__(self, id, date, round, home_team, away_team, home_score, away_score, status,minute,referee,country):
        """
        Class for structure data of a match.

        Args:
            id (int): unique identifier of the match
            date (str): date of the match
            home_team (Team): team at home
            away_team (Team): team away
            home_score (int): score of the team at home
            away_score (int): score of the team away
        """
        self.id = id
        self.date = date
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = home_score
        self.away_score = away_score
        self.status = status
        self.minute = minute
        self.referee = referee
        self.round = round
        self.country = country

    def __str__(self) -> str:
        # Tronca o aggiunge spazi ai nomi delle squadre
        team1_str = f"{self.home_team[:20]:<20}"
        team2_str = f"{self.away_team[:20]:<20}"
        
        # Format punteggio, stato e minuto (gestisce extra_time)
        score_team1_str = f"{self.home_score:>2}" if self.home_score != None else " -"
        score_team2_str = f"{self.away_score:>2}" if self.away_score != None else " -"
        
        if self.minute != None:
            if self.minute > 90:
                minute_str = f"90+{(self.minute - 90):>2}"  # Formato per minuti supplementari
            else:
                minute_str = f"{self.minute:>3}"  # Minuti normali
        else:
            minute_str = " - "  # if the minute is None, set it to "  "
        status_str = f"{self.status[:2]:<2}"
        if self.status == "HT" or self.status == "2H" or self.status == "1H":
            #mark colored ballon for live matches
            livestatus = "●LIVE"
        else:
            livestatus = " "
        
        # Format data e ora (15 caratteri)
        datetime_str = datetime.fromisoformat(self.date).strftime("%d/%m/%Y %H:%M")
        country_str = f"{self.country[:15]:<15}"
        
        # Costruisci la stringa finale con 1 spazio tra minuto, stato e data
        result = f"{team1_str}{team2_str}{score_team1_str}{score_team2_str} {minute_str} {status_str} {datetime_str} | {country_str} {livestatus}"
        
        return result


    #function to get fixture data

class Event:
    def __init__(self,team,event,minute,player,assist,comment) -> None:
        self.team = team
        self.event = event
        self.minute = minute
        self.player = player
        self.assist = assist
        self.comment = comment
        
class Stats:
    def __init__(self,team_name,shots_on_goal,shots_off_goal,shots_insidebox,shots_outsidebox,total_shots,
                 blocked_shots,fouls,corners_kicks,offsides,ball_possession,yellow_card,red_card,
                 goalkeepers_saves,total_passes,passes_accurate,passes_percentage) -> None:
        # self.team_name = {"team_name":team_name}
        # self.shots_on_goal = {"shots_on_goal":shots_on_goal}
        # self.shots_off_goal = {"shots_off_goal":shots_off_goal}
        # self.shots_insidebox = {"shots_insidebox":shots_insidebox}
        # self.shots_outsidebox = {"shots_outsidebox":shots_outsidebox}
        # self.total_shots = {"total_shots":total_shots}
        # self.blocked_shots = {"blocked_shots":blocked_shots}
        # self.fouls = {"fouls":fouls}
        # self.corners_kicks = {"corners_kicks":corners_kicks}
        # self.offsides = {"offsides":offsides}
        # self.ball_possession = {"ball_possession":ball_possession}
        # self.yellow_card = {"yellow_card":yellow_card}
        # self.red_card = {"red_card":red_card}
        # self.goalkeepers_saves = {"goalkeepers_saves":goalkeepers_saves}
        # self.total_passes = {"total_passes":total_passes}
        # self.passes_accurate = {"passes_accurate":passes_accurate}
        # self.passes_percentage = {"passes_percentage":passes_percentage}
        self.team_name = team_name
        self.shots_on_goal = shots_on_goal
        self.shots_off_goal = shots_off_goal
        self.shots_insidebox = shots_insidebox
        self.shots_outsidebox = shots_outsidebox
        self.total_shots = total_shots
        self.blocked_shots = blocked_shots
        self.fouls = fouls
        self.corners_kicks = corners_kicks
        self.offsides = offsides
        self.ball_possession = ball_possession
        self.yellow_card = yellow_card
        self.red_card = red_card
        self.goalkeepers_saves = goalkeepers_saves
        self.total_passes = total_passes
        self.passes_accurate = passes_accurate
        self.passes_percentage = passes_percentage

class Player:
    def __init__(self,name,position,role,number) -> None:
        self.name = name
        self.role = role
        self.position = position
        self.number = number

class Formation:
    def __init__(self,team_name,formation,Player,coach) -> None:
        self.team_name = team_name
        self.formation = formation
        self.player = Player
        self.coach = coach