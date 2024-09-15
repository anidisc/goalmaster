from typing import Coroutine
from textual.events import AppFocus, Key
import gemini_ai
import api_football as af
from textual.app import App
from textual.widgets import Header, Footer, Button, Static, Input, OptionList, Collapsible
from textual.containers import ScrollableContainer, Vertical
from rich import print as rich_print
from _datetime import datetime,timedelta
import shlex


APPVERSION = "0.0.4"
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
    CSS_PATH = "appstyle.tcss"


    def __init__(self):
        super().__init__()
        self.YEAR_SELECT = af.ApiFootball().YEAR
        self.league_selected = 0
        #create a dict of all list of fixtures to reference them later
        self.blocklist = {}
        self.list_of_blocks = []

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
        self.input_box.styles.visibility = "hidden" # Hide the input box
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        block = Static(standings,id=block_id+"_standings", name="block",classes="block")
        block.border_title = f"Standings {self.find_league(league)}"
        self.query_one("#main_container").mount(Collapsible(block,id=block_id,title=block.border_title,collapsed=False))
        self.query_one("#main_container").scroll_end()
        self.query_one(f"#{block_id}").focus()
    def add_block_fixture(self,datefrom,dateto,live=False):
        self.input_box.styles.visibility = "hidden" # Hide the input box
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
        self.input_box.styles.visibility = "hidden" # Hide the input box
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

    def on_mount(self):
        self.query_one("#input").styles.visibility = "hidden" # 
        self.title = f"GOAL MASTER {APPVERSION} YEAR:{af.ApiFootball().YEAR} CALLS:{af.ApiFootball().get_status_apicalls()}"
        # self.boxmessage = self.query_one("#infolayout")
        # self.boxmessage.styles.visibility = "hidden"
        self.query_one("#main_container").focus()
    #make a function that show a message in the infobox
    # def show_message(self,text,titlebox=""):
    #     self.boxmessage.styles.visibility = "visible"
    #     self.boxmessage.border_title = titlebox
    #     self.infobox.update(text)
    #     self.query_one("#ok_info_button").focus()
        
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
    #button pressed
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok_info_button":
            self.boxmessage.styles.visibility = "hidden"
            self.screen.focus()
    def action_insert_command(self):
        self.input_box.styles.visibility = "visible" if self.input_box.styles.visibility == "hidden" else "hidden"
        self.input_box.focus()
    def action_change_year(self):
        self.yearsbox.styles.visibility = "visible" if self.yearsbox.styles.visibility == "hidden" else "hidden"
        self.yearsbox.focus()
    def on_input_submitted(self, event: Input.Submitted):
        #validate di input is not void
        if event.value == "":
            return
        command = shlex.split(event.value.upper()) # Split the input string into a list of words
        #hide input box
        self.input_box.styles.visibility = "hidden"
        #check if command is valid
        if command[0] == "LIVE":
            self.add_block_fixture(datetime.now().date(),datetime.now().date(),live=True)
            # show live matches define in ApiFootball and function get_fixture_live
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
                self.add_block_standings(self.league_selected)
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
                self.notify("error command syntax",severity="error",timeout=10)
        else:
            #self.show_message("command not found",titlebox="INVALID COMMAND")
            self.notify("command not found",severity="error",timeout=10)
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
        if event.option_list.id == "yearsbox":
            selected_option = event.option.prompt
            self.yearsbox.border_subtitle = selected_option
            self.yearsbox.styles.visibility = "hidden"
            self.YEAR_SELECT = selected_option
            self.title = f"GOAL MASTER {APPVERSION} YEAR:{self.YEAR_SELECT} CALLS:{af.ApiFootball().get_status_apicalls()}"
            return
        if event.option_list.id in self.list_of_blocks:
            selec_match = self.blocklist[event.option_list.id][event.option_index]
            self.notify(selec_match.home_team+" vs "+selec_match.away_team,severity="info",timeout=5)
            #TODO show live matches in the future
            self.add_block_events_match(selec_match.id,selec_match.home_team,selec_match.away_team)

if __name__ == "__main__":
    app = goalmasterapp().run()

