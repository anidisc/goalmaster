#!/usr/bin/env python3

import json
import os
from typing import Coroutine
from pyparsing import NoMatch
from textual.events import AppFocus, Key
import gemini_ai
import api_football as af
from textual.app import App
from textual.widgets import Header, Footer, Button, Static, Input, OptionList, Collapsible
from textual.containers import ScrollableContainer, Vertical,Horizontal
from rich import print as rich_print
from rich.markdown import Markdown
from rich.table import Table
from _datetime import datetime,timedelta
import shlex
from io import StringIO
from rich.console import Console
import gm_data as gm


APPVERSION = "0.1.7"
af_map={
    "SERIEA":{"id":135,"name":"Serie A","country":"Italy"},
    "LALIGA":{"id":140,"name":"LaLiga","country":"Spain"},
    "BUNDESLIGA":{"id":78,"name":"Bundesliga","country":"Germany"},
    "LIGUE1":{"id":61,"name":"Ligue 1","country":"France"},
    "PREMIERLEAGUE":{"id":39,"name":"Premier League","country":"England"},
    "SERIEB":{"id":136,"name":"Serie B","country":"Italy"},
    "BUNDESLIGA2":{"id":79,"name":"Bundesliga 2","country":"Germany"},
    "LIGUE2":{"id":62,"name":"Ligue 2","country":"France"},
    "SUPERLIG":{"id":203,"name":"Super Lig","country":"Turkey"},
    "UCL":{"id":2,"name":"UEFA Champions League","country":"Europe"},
    "UEL":{"id":3,"name":"UEFA Europa League","country":"Europe"},
    "UNL":{"id":5,"name":"UEFA Nations League","country":"Europe"},
    "ERE":{"id":88,"name":"Eredivisie","country":"Netherlands"},
    "COPPAITALIA":{"id":142,"name":"Coppa Italia","country":"Italy"},
}
def table_af_map():
    #print a table with the a columm for keys and names if leagues
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key", style="dim", width=12)
    table.add_column("Name", min_width=20)
    table.add_column("Country", min_width=12)

    for key, value in af_map.items():
        table.add_row(key, value['name'], value['country'])

    console = Console(record=True, width=100)
    console.print(table)
    return console.export_text()
#class for structure data of a soccer team
class goalmasterapp(App):
    BINDINGS = [("q", "quit", "Quit"),
                ("y", "change_year", "Change Year"),
                ("i", "insert_command", "Insert Command"),
                ("r","remove_block","Remove Block"),
                ("c", "collapse_or_expand(True)", "Collapse All")]
    CSS_PATH = "appstyle.tcss"


    def __init__(self):
        super().__init__()
        self.YEAR_SELECT = af.ApiFootball().YEAR
        self.league_selected = 0
        #create a dict of all list of fixtures to reference them later
        self.blocklist = {}
        self.list_of_blocks = []
        self.selec_match = []
        self.last_focus_id =None
        self.memory_standings = None  # Memory of the standings in list of dict

    def compose(self):
        yield Header()
        yield ScrollableContainer(id="main_container")
        yield Footer()
        self.block_counter = 0  # Counter for block id and number of blocks
        self.input_box=Input(id="input", name="input", placeholder="Insert Command")
        yield self.input_box
        self.yearsbox=OptionList("2020","2021","2022","2023","2024",id="yearsbox")
        self.yearsbox.border_title = "Select Year"
        yield self.yearsbox
        #create an info box to show a varius texts
        # self.infobox = Static("info text to print",id="infobox")
        # yield Vertical(self.infobox,Button("ok",id="ok_info_button"),id="infolayout") 
        self.select_todo_box = OptionList("EVENT TABLE","MATCH STATS","PREDICTION","FORM.LINEUPS","EXIT",id="select_todo_box")
        yield self.select_todo_box
    def find_league(self,league):
            #find name of league with de id of league
        for k,v in af_map.items():
            if v["id"] == self.league_selected:
                league_name = f"{af_map[k]["name"]} Country: {af_map[k]["country"]}"
                break 
        return league_name
    
    #create block to show the current standings of the league
    def add_block_standings(self,league,text="text to print",group=0):
        s = af.ApiFootball(self.YEAR_SELECT).get_list_standings(self.league_selected)
        if group =="all":
            standings = [af.ApiFootball().get_table_standings(x) for x in s]
        else:
            standings = [af.ApiFootball().get_table_standings(s[group])]
        #self.input_box.styles.visibility = "hidden" # Hide the input box
        self.block_counter += 1 # Increment the block counter
        block=[] #block of standigs
        block_id = f"block_{self.block_counter}" # Create a unique block id
        idcounter = 0
        for b in standings:
            bid=f"{block_id}_{idcounter}_{group}"
            block.append(Static(b,id=bid,classes="block"))
            idcounter += 1

        if len(block) <= 1:
            block_standings_pile = block[0]
        else:
            block_standings_pile = ScrollableContainer(*block)

        content_title = f"Standings {self.find_league(league)}"
        self.query_one("#main_container").mount(Collapsible(block_standings_pile,id=block_id,title=content_title,collapsed=False))
        self.query_one("#main_container").scroll_end()
        self.query_one(f"#{block_id}").focus()
    def add_block_fixture(self,datefrom,dateto,live=False):
        #self.input_box.styles.visibility = "hidden" # Hide the input box
        fixtures=af.ApiFootball().get_list_fixtures(self.league_selected,datefrom,dateto,live)
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        self.list_of_blocks.append(block_id)  #create e registry of blocks
        #save blocklist in a dict
        self.blocklist[block_id] = fixtures
        #list_fixtures = ListView(*[ListItem(Static(str(fix)),classes="item_match") for fix in fixtures],id=f"block_{self.block_counter}",classes="block2")
        list_fixtures = OptionList(*[str(fix) for fix in fixtures],id=block_id,classes="block2")
        list_fixtures_title = f"Fixtures League: {self.find_league(self.league_selected)}" if live == False else "Live Fixtures ALL COUNTRIES"
        list_fixtures.border_subtitle = f"from:{datefrom} - to:{dateto}"

        self.query_one("#main_container").mount(Collapsible(list_fixtures,
                                                            id=block_id+"_fixtures",title=list_fixtures_title,
                                                            collapsed=False)) #mount block and list_fixtures)
        #focus on list view
        list_fixtures.focus()
        #scrool maioncontainer on botton of list view
        self.query_one("#main_container").scroll_end()
    def add_block_events_match(self,id_fixture,team1,team2):
        #self.input_box.styles.visibility = "hidden" # Hide the input box
        events_table=af.ApiFootball().get_table_event_flow(id_fixture)
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        self.query_one("#main_container").mount(Collapsible(Static(events_table),
                                                            id=block_id,title="Events Match: "+team1+" vs "+team2,
                                                            collapsed=False)) #mount block and list_fixtures)
        #focus on list view
        #events.focus()
        #scrool maioncontainer on botton of list view
        self.query_one("#main_container").scroll_end()
    
    def add_block_stats_match(self,id_fixture,team1,team2):
        #self.input_box.styles.visibility = "hidden" # Hide the input box
        stats_table=af.ApiFootball().print_table_standings(id_fixture)
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        self.query_one("#main_container").mount(Collapsible(Static(stats_table),
                                                            id=block_id,title="Statistic Match: "+team1+" vs "+team2,
                                                            collapsed=False)) #mount block and list_fixtures)
        self.query_one("#main_container").scroll_end()

    def add_block_prediction(self,league_id,id_fixture,team1,team2,prompt):
        #self.input_box.styles.visibility = "hidden" # Hide the input box
        json_file = gm.PREDICTION_FILE_DB
        id_fixture = str(id_fixture) #convert to string
        # Check if the file exists
        if not os.path.exists(json_file):
            predictions = {}  # Create an empty dictionary if the file doesn't exist
        else:
            # Load the existing predictions from the file
            with open(json_file, "r") as f:
                predictions = json.load(f)
        
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        table_stats=af.ApiFootball().get_standings(league_id)
        composed_prompt = f"The match is between {team1} vs {team2}, and view this standing: {table_stats}"
        if id_fixture in predictions:
            prediction = predictions[id_fixture]
        else:
            prediction=gemini_ai.gemini_ai_call(composed_prompt+prompt) 
            # Save the updated predictions back to the JSON file with indentation for readability
            predictions[id_fixture] = prediction
            with open(json_file, "w") as f:
                json.dump(predictions, f, indent=4) 
        self.query_one("#main_container").mount(Collapsible(Static(Markdown(prediction),classes="predictions"),
                                                            id=block_id,title="Prediction Match: "+team1+" vs "+team2,
                                                            collapsed=False)) #mount block and list_fixtures)
        self.query_one("#main_container").scroll_end()
  

    def add_block_formations(self,id_fixture,team1,team2):
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        #f1,f2=af.ApiFootball().get_formation_teams(id_fixture)
        formtext=af.ApiFootball().print_table_formations(id_fixture)
        self.query_one("#main_container").mount(Collapsible(Static(formtext),id=block_id,title=f"Formations: {team1} vs {team2}",collapsed=False))
        self.query_one("#main_container").scroll_end()
    
    def add_block_help(self):
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        tabmap=table_af_map()
        formatted_tabmap = tabmap.split("\n")[0] + "\n" +"\n".join("            " + line for line in tabmap.split("\n")[1:])
        HELPTEXT=f"""

        GOAL MASTER {APPVERSION} YEAR:{af.ApiFootball().YEAR} CALLS:{af.ApiFootball().get_status_apicalls()}

        KEYBOARD SHORTCUTS:

        TAB - Switch between input and select todo boxes
        ENTER - Add new todo
        Press r - Remove focused block

        INPUT BOX:
        command:
        -LIVE - show live matches define in ApiFootball and function get_fixture_live
        -HELP - show this help
        -LEAGUE -args: 
            -S - standings
            -T - timeshift days (example 1 is from today to today+1, or -1 is from today to today-1)
        Available LEAGUES:

            {formatted_tabmap}
        
        Press q - Exit

        
        """
        self.query_one("#main_container").mount(Collapsible(Static(HELPTEXT),id=block_id,title="Help",collapsed=False))
        self.query_one("#main_container").scroll_end()

    def on_mount(self):
        #self.query_one("#input").styles.visibility = "hidden" # 
        self.input_box.display = False # Hide the input box
        #self.select_todo_box.styles.visibility = "hidden" # hide the select todo box
        self.select_todo_box.display = False
        self.title = f"GOAL MASTER {APPVERSION} YEAR:{af.ApiFootball().YEAR} CALLS:{af.ApiFootball().get_status_apicalls()}"
        # self.boxmessage = self.query_one("#infolayout")
        # self.boxmessage.styles.visibility = "hidden"
        self.query_one("#main_container").focus()

    # async def on_focus(self, event):
    #     self.last_focus_id = event.app.focused.id if event.app.focused else None
    #     #create a list of id of focus widgets
    #     #self.last_focus_id = event.id
    #     self.title = self.last_focus_id if self.last_focus_id else "GOAL MASTER"

    def on_key(self, event: Key):
        if event.key == "a":
            pass
            # self.YEAR_SELECT = af.ApiFootball().YEAR
            # self.add_block_standings(self.league_selected)
        if event.key == "r" and self.block_counter > 0:
            # widget_id_to_remove =f"block_{self.block_counter}"
            if self.focused.id == self.query_one("#main_container").id:
                return None
            if self.focused:
                self.focused.parent.remove()
            #self.query_one(f"#{widget_id_to_remove}").remove()
            #self.block_counter -= 1
            #exit app if no block is left
            if self.block_counter == 0:
                self.exit()
    #button pressed

    def action_insert_command(self):
        #self.input_box.styles.visibility = "visible" if self.input_box.styles.visibility == "hidden" else "hidden"
        self.input_box.display = True
        self.input_box.focus()
    def action_change_year(self):
        self.yearsbox.styles.visibility = "visible" if self.yearsbox.styles.visibility == "hidden" else "hidden"
        self.yearsbox.focus()
    def action_collapse_or_expand(self, collapse: bool) -> None:
        for child in self.walk_children(Collapsible):
            child.collapsed = collapse

    def on_input_submitted(self, event: Input.Submitted):
        #validate di input is not void
        if event.value == "":
            return
        command = shlex.split(event.value.upper()) # Split the input string into a list of words
        #hide input box
        #self.input_box.styles.visibility = "hidden"
        #check if command is valid
        if command[0] == "LIVE":
            self.add_block_fixture(datetime.now().date(),datetime.now().date(),live=True)
            self.input_box.display = False
            # show live matches define in ApiFootball and function get_fixture_live
            return
        if command[0] == "HELP":
            self.add_block_help()
            self.input_box.display = False
            return
        if command[0] == "EXIT":
            self.exit()
            return
        if command[0] == "X":  #if command is empty close input box
            self.input_box.display = False
            return

        if command[0] in af_map:
            self.league_selected = af_map[command[0]]["id"]
            #check if command is valid
            if len(command) == 1:
                self.notify(f"insert options command for {self.find_league(self.league_selected)}",severity="warning",timeout=10)
                # self.show_message(f"insert options command for {self.find_league(self.league_selected)}",
                #                   titlebox=f"IMCOMPLETE COMMAND")
                return
            if command[1] == "-S":
                #check if exist command[2]
                if len(command) < 3:
                    self.add_block_standings(self.league_selected)
                else:
                    if command[2] == "ALL":
                        self.add_block_standings(self.league_selected,group="all")
                    elif int(command[2]) in range(10):
                        self.add_block_standings(self.league_selected,group=int(command[2]))
                    else:
                        #self.show_message("error command syntax",titlebox="SYNTAX ERROR")
                        self.notify("error command syntax",severity="error",timeout=5)
            elif command[1] == "-T":
                if len(command) < 3:
                    command.append("0")  #default value for days
                #validate if the time parameter is valid in range -150 to 150
                if -150 <= int(command[2]) <= 150:
                    if int(command[2]) >= 0:
                        dfrom=datetime.now().date()
                        dto=datetime.now().date()+timedelta(days=int(command[2]))
                        self.add_block_fixture(dfrom,dto)
                    elif int(command[2]) < 0:
                        dfrom=datetime.now().date()+timedelta(days=int(command[2]))
                        dto=datetime.now().date()
                        self.add_block_fixture(dfrom,dto)
            else:
                #self.show_message("error command syntax",titlebox="SYNTAX ERROR")
                self.notify("error command syntax",severity="error",timeout=5)
        else:
            #self.show_message("command not found",titlebox="INVALID COMMAND")
            self.notify("command not found",severity="error",timeout=5)
            # self.add_block_standings(self.league_selected)   

        # if command == "seriea":
        #     self.league_selected = 135
        #     self.add_block_standings(self.league_selected)
        # elif command == "ligue1":
        #     self.league_selected = 61
        #     self.add_block_standings(self.league_selected)
        # elif command == "bundesliga":
        #     self.league_selected = 78
        #     self.add_block_standings(self.league_selected)

        #self.input_box.styles.visibility = "hidden"
        self.input_box.display = False # Hide the input box
        self.input_box.value = ""
 
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id == "yearsbox":
            selected_option = event.option.prompt
            self.yearsbox.border_subtitle = selected_option
            self.yearsbox.styles.visibility = "hidden"
            self.YEAR_SELECT = selected_option
            self.title = f"GOAL MASTER {APPVERSION} YEAR:{self.YEAR_SELECT} CALLS:{af.ApiFootball().get_status_apicalls()}"
            return
        if event.option_list.id in self.list_of_blocks:
            self.selec_match = self.blocklist[event.option_list.id][event.option_index]
            # if self.selec_match.status in ["NS","RS"]: #not started or resulted
            #     self.notify("match not started yet",severity="warning",timeout=5)
            #     #self.select_todo_box.styles.visibility = "hidden"

            #     self.screen.focus()
            #     return
            #self.select_todo_box.styles.visibility = "visible" #show select todo box
            self.select_todo_box.display = True
            #focus on select todo box
            self.select_todo_box.focus()
            

            self.notify(self.selec_match.home_team+" vs "+self.selec_match.away_team,severity="info",timeout=5)
            #TODO show live matches in the future
        if event.option_list.id == "select_todo_box":
            # if self.selec_match.status in ["NS","RS"]: #not started or resulted
            #     self.notify("match not started yet",severity="warning",timeout=5)
            #     self.select_todo_box.styles.visibility = "hidden"
            #     self.screen.focus()
            #     return
            #self.select_todo_box.styles.visibility = "hidden"
            self.select_todo_box.display = False
            if event.option_index == 0:  #selected add block events events of the match
                if self.selec_match.status in ["NS","RS"]: #not started or resulted
                    self.notify("match not started yet",severity="warning",timeout=5)
                    #self.select_todo_box.styles.visibility = "hidden"
                    self.focused.focus()
                    return
                self.add_block_events_match(self.selec_match.id,self.selec_match.home_team,self.selec_match.away_team)
            if event.option_index == 1:  #selected add block stats of the match
                if self.selec_match.status in ["NS","RS"]: #not started or resulted
                    self.notify("match not started yet",severity="warning",timeout=5)
                    #self.select_todo_box.styles.visibility = "hidden"
                    self.focused.focus()
                    return
                self.add_block_stats_match(self.selec_match.id,self.selec_match.home_team,self.selec_match.away_team)
            if event.option_index == 2:  #selected add block standings of the league
                prompt_request = f"""
                Analyze the match between {self.selec_match.home_team} and {self.selec_match.away_team}.
                Try to analyze the match between the two teams, providing a precise context in which they 
                will face each other, comparing their statistical performance in the league. 
                Present this data using comparative tables and histograms where possible. 
                Analyze well the behavior and performance of the teams at home and away, and base your judgment on this, 
                which should be a calculated prediction 1 X 2, and where you are unsure, also provide a double chance 
                (for example, 1X, X2, 12). Additionally, separate with a line the next judgment on how many 
                goals the teams might score and whether it's likely to be GG (both teams to score) or NG 
                (no goals from one or both teams). Further, 
                identify the team with the highest probability of scoring at least one goal, which should exceed 70%, 
                and the team with the lowest probability of scoring at least one goal, which should be below 30%. and of course, explain all your choices."

                """
                # if not (self.selec_match.status in ["NS","RS"]): #not started or resulted
                #     self.notify("Match not started",severity="warning",timeout=5)
                if self.selec_match.status == "FT":
                    self.notify("Match finished",severity="warning",timeout=5)
                elif self.selec_match.status in ["1H","2H","HT","P"]: #live prediction
                    self.notify("Match live",severity="warning",timeout=5)
                    pass
                else:  #not live prediction
                    self.notify(f"Analyze prediction... {self.selec_match.home_team} vs {self.selec_match.away_team}",severity="info",timeout=8)
                    self.add_block_prediction(self.league_selected,self.selec_match.id,self.selec_match.home_team,self.selec_match.away_team,prompt_request)
                    #update flag prediction match to true
                    self.selec_match.prediction = True
            if event.option_index == 3:  #selected add block formations of selected match
                if not (self.selec_match.status in ["NS","RS"]): #not started or resulted
                    self.add_block_formations(self.selec_match.id,self.selec_match.home_team,self.selec_match.away_team)
                else:
                    self.notify("Match not started",severity="warning",timeout=5)
                    self.focused.focus()
                    
                    return
if __name__ == "__main__":
    app = goalmasterapp().run()

