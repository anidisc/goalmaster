#data structure of the app

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
        return (self.goals_for) / self.matches
    def medius_goals_against(self):
        #medius between goals for in the matches and goals against in the number of matches
        return (self.goals_against) / self.matches
    def goal_difference(self):
        """
        Calculate the difference between the goals scored by the team and the goals scored against the team.
        
        Returns:
            int: The difference between the goals scored by the team and the goals scored against the team.
        """
        return self.goals_for - self.goals_against
    #medius between goals for home
    def medius_goals_for_home(self):
        return (self.goals_for_home) / self.matches
    #medius between goals for away
    def medius_goals_for_away(self):
        return (self.goals_for_away) / self.matches
    

