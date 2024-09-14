from typing import Coroutine
from textual.events import AppFocus, Key
import gemini_ai
import api_football as af
from textual.app import App
from textual.widgets import Header, Footer, Button, Static, ListView, ListItem, Input, OptionList
from textual.containers import ScrollableContainer
from rich import print as rich_print
from _datetime import datetime,timedelta
import shlex


APPVERSION = "0.0.3"
af_map={
    "SERIEA":{"id":135,"name":"Serie A","country":"Italy"},
    "LALIGA":{"id":140,"name":"LaLiga","country":"Spain"},
    "BUNDESLIGA":{"id":78,"name":"Bundesliga","country":"Germany"},
    "LIGUE1":{"id":61,"name":"Ligue 1","country":"France"},
    "PREMIERLEAGUE":{"id":39,"name":"Premier League","country":"England"},
    "SERIEB":{"id":136,"name":"Serie B","country":"Italy"},
    "BUNDESLIGA2":{"id":79,"name":"Bundesliga 2","country":"Germany"},
    "LIGUE2":{"id":62,"name":"Ligue 2","country":"France"},
}

#class for structure data of a soccer team
class goalmasterapp(App):
    BINDINGS = [("q", "quit", "Quit"),
                ("y", "change_year", "Change Year"),
                ("i", "insert_command", "Insert Command"),
                ("r","remove_block","Remove Block")]
    CSS_PATH = "appstyle.css"

    
    def __init__(self):
        super().__init__()
        self.YEAR_SELECT = af.ApiFootball().YEAR
        self.league_selected = 135
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

    def find_league(self,league):
            #find name of league with de id of league
        for k,v in af_map.items():
            if v["id"] == self.league_selected:
                league_name = f"{af_map[k]["name"]} Country: {af_map[k]["country"]}"
                break 
        return league_name
    
    #create block to show the current standings of the league
    def add_block_standings(self,league,text="text to print"):
        standings = af.ApiFootball(self.YEAR_SELECT).get_table_standings(league)
        #standings=text
        self.input_box.styles.visibility = "hidden" # Hide the input box
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        block = Static(standings,id=block_id, name="block",classes="block")
        block.border_title = f"Standings {self.find_league(league)}"
        self.query_one("#main_container").mount(block)
        self.query_one("#main_container").scroll_end()
    def add_block_fixture(self,datefrom,dateto):
        self.input_box.styles.visibility = "hidden" # Hide the input box
        fixtures=af.ApiFootball().get_list_fixtures(self.league_selected,datefrom,dateto)
        self.block_counter += 1 # Increment the block counter
        list_fixtures = ListView(*[ListItem(Static(str(fix)),name="item_match") for fix in fixtures],id=f"block_{self.block_counter}",classes="block2")
        list_fixtures.border_title = f"Fixtures League: {self.find_league(self.league_selected)}"
        list_fixtures.border_subtitle = f"from:{datefrom} - to:{dateto}"

        self.query_one("#main_container").mount(list_fixtures)
        #focus on list view
        list_fixtures.focus()
        #scrool maioncontainer on botton of list view
        self.query_one("#main_container").scroll_end()
    def on_mount(self):
        #self.add_block_standings(self.league_selected)
        self.query_one("#input").styles.visibility = "hidden" # 
        self.title = f"GOAL MASTER {APPVERSION} YEAR:{af.ApiFootball().YEAR} CALLS:{af.ApiFootball().get_status_apicalls()}"
        #self.yearsbox.styles.visibility = "hidden"
        self.query_one("#main_container").focus()
    def on_key(self, event: Key):
        if event.key == "a":
            self.YEAR_SELECT = af.ApiFootball().YEAR
            self.add_block_standings(self.league_selected)
        if event.key == "r" and self.block_counter > 0:
            widget_id_to_remove =f"block_{self.block_counter}"
            self.query_one(f"#{widget_id_to_remove}").remove()
            self.block_counter -= 1
            #exit app if no block is left
            if self.block_counter == 0:
                self.exit()
    def action_insert_command(self):
        self.input_box.styles.visibility = "visible" if self.input_box.styles.visibility == "hidden" else "hidden"
        self.input_box.focus()
    def action_change_year(self):
        self.yearsbox.styles.visibility = "visible" if self.yearsbox.styles.visibility == "hidden" else "hidden"
        self.yearsbox.focus()
    def on_input_submitted(self, event: Input.Submitted):

        command = shlex.split(event.value.upper())
        #self.add_block_standings(self.league_selected,text=command[0]+" "+command[1])    
        #verify if the command input is in the keys od dictionary af_map
        if command[0] in af_map:
            self.league_selected = af_map[command[0]]["id"]
            if command[1] == "-S":
                self.add_block_standings(self.league_selected)
            elif command[1] == "-T":
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
                pass
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

        self.input_box.styles.visibility = "hidden"
        self.input_box.value = ""
 
    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        
        elected_option = event.option.prompt
        self.yearsbox.border_subtitle = elected_option
        self.yearsbox.styles.visibility = "hidden"
        self.YEAR_SELECT = elected_option
        self.title = f"GOAL MASTER {APPVERSION} YEAR:{self.YEAR_SELECT} CALLS:{af.ApiFootball().get_status_apicalls()}"
if __name__ == "__main__":
    app = goalmasterapp().run()

