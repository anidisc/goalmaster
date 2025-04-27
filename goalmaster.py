#!/usr/bin/env python3

import json
import os
# from typing import Coroutine
# from pyparsing import NoMatch
from textual.events import Key
import gemini_ai
import api_football
from textual.app import App
from textual.widgets import Header, Footer, Static, Input, OptionList, Collapsible
from textual.containers import ScrollableContainer, HorizontalScroll
from rich import print as rich_print
from rich.markdown import Markdown
from rich.table import Table
from _datetime import datetime,timedelta
import shlex
#from io import StringIO
from rich.console import Console
import gm_data as gm
from markdown import markdown
from weasyprint import HTML
import mistune


APPVERSION = "0.8.5"
af_map={
    "SERIEA":{"id":135,"name":"Serie A","country":"Italy"},
    "LALIGA":{"id":140,"name":"LaLiga","country":"Spain"},
    "BUNDESLIGA":{"id":78,"name":"Bundesliga","country":"Germany"},
    "LIGUE1":{"id":61,"name":"Ligue 1","country":"France"},
    "PREMIERLEAGUE":{"id":39,"name":"Premier League","country":"England"},
    "LIGA":{"id":141,"name":"Liga Purtugal","country":"Portugal"},
    "PRIMERA":{"id":137,"name":"Primera División","country":"Spain"},
    "SERIEB":{"id":136,"name":"Serie B","country":"Italy"},
    "SERIEC1":{"id":138,"name":"Serie C","country":"Italy"},
    "SERIEC2":{"id":942,"name":"Serie C","country":"Italy"},
    "SERIEC3":{"id":943,"name":"Serie C","country":"Italy"},
    "BUNDESLIGA2":{"id":79,"name":"Bundesliga 2","country":"Germany"},
    "LIGUE2":{"id":62,"name":"Ligue 2","country":"France"},
    "SUPERLIG":{"id":203,"name":"Super Lig","country":"Turkey"},
    "UCL":{"id":2,"name":"UEFA Champions League","country":"Europe"},
    "UEL":{"id":3,"name":"UEFA Europa League","country":"Europe"},
    "UNL":{"id":5,"name":"UEFA Nations League","country":"Europe"},
    "ERE":{"id":88,"name":"Eredivisie","country":"Netherlands"},
    "COPPAITALIA":{"id":142,"name":"Coppa Italia","country":"Italy"},
    # Additional European championships
    "SCOTTISHPREM":{"id":179,"name":"Premiership","country":"Scotland"},
    "BELGIANPRO":{"id":144,"name":"Jupiler Pro League","country":"Belgium"},
    "SUPERLEAGUE":{"id":197,"name":"Super League","country":"Switzerland"},
    "AUSTRIANBL":{"id":218,"name":"Bundesliga","country":"Austria"},
    "GREEKSL":{"id":207,"name":"Super League","country":"Greece"},
    "DANISHSL":{"id":119,"name":"Superliga","country":"Denmark"},
    "RUSSIANPL":{"id":235,"name":"Premier League","country":"Russia"},
    "CROATIANHNL":{"id":210,"name":"HNL","country":"Croatia"},
    "NORWEGIANL":{"id":103,"name":"Eliteserien","country":"Norway"},
    "SWEDISHALLSV":{"id":113,"name":"Allsvenskan","country":"Sweden"},
    "CONFERENCELEA":{"id":848,"name":"UEFA Conference League","country":"Europe"},
}

languege="italian"  #set here the language for the analysis of predictions

af = api_football.ApiFootball()

from PyPDF2 import PdfMerger
from datetime import datetime

def merge_pdfs(id_league,id_fixtures, output_folder="pdf/reports/") -> bool:
    input_folder = "pdf/predictions/"
    date_of_report=datetime.now().strftime("%Y-%m-%d")
    merger = PdfMerger()
    
    flagmerge=False
    for id_fixture in id_fixtures:
        pdf_path = os.path.join(input_folder, f"{id_fixture}.pdf")
        if os.path.exists(pdf_path):
            merger.append(pdf_path)
            flagmerge=True
     
    if not flagmerge:
        return False
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_file = os.path.join(output_folder, f"report_{id_league}_{datetime.today().strftime('%Y-%m-%d')}.pdf")
    merger.write(output_file)
    merger.close()
    #print(f"PDF unito creato: {output_file}")
    return True


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

#create a function to save the prediction in a file pdf named with che id_fixture.pdf
def save_prediction_pdf(id_fixture,prediction):
    #save the prediction in a file pdf named with che id_fixture.pdf
    pathfilepdf=f"pdf/predictions/{id_fixture}.pdf"
    try:
        # Converti il Markdown in HTML
        html_content = markdown(prediction, extensions=['tables'])

        # Aggiungi uno stile CSS base per migliorare l'aspetto delle tabelle
        css = """
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
        """
        cssmini = """
        body {
            font-family: Arial, sans-serif;
            font-size: 10px;
            margin: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 9px;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 4px;
        }
        th {
            background-color: #f9f9f9;
            font-weight: bold;
        }
        h1, h2, h3, h4, h5, h6 {
            margin: 5px 0;
        }
        p {
            margin: 5px 0;
        }
        """

        # Combina l'HTML e lo stile CSS
        full_html = f"""
        <html>
        <head>
        <style>{cssmini}</style>
        </head>
        <body>
        {html_content}
        </body>
        </html>
        """

        # Genera il PDF usando WeasyPrint
        HTML(string=full_html).write_pdf(pathfilepdf)
    except Exception as e:
        pass

    # Converti il testo iniziale in HTML
    # markdown_renderer = mistune.create_markdown()
    # html_content = markdown_renderer(prediction)
    # # Applica CSS
    # custom_css = """
    #                     table {
    #                         width: 100%;
    #                         border-collapse: collapse;
    #                         margin: 20px 0;
    #                         font-size: 16px;
    #                         text-align: left;
    #                     }
    #                     th, td {
    #                         border: 1px solid #dddddd;
    #                         padding: 8px;
    #                     }
    #                     th {
    #                         background-color: #f2f2f2;
    #                     }
    #                     body {
    #                         font-family: Arial, sans-serif;
    #                         line-height: 1.6;
    #                         margin: 20px;
    #                     }
    #                     """
    # html_content = f"<style>{custom_css}</style>{html_content}"
    # HTML(string=html_content).write_pdf(pathfilepdf)
    return

#class for structure data of a soccer team
class goalmasterapp(App):
    BINDINGS = [("q", "quit", "Quit"),
                ("y", "change_year", "Change Year"),
                ("i", "insert_command", "Insert Command"),
                ("r","remove_block","Remove Block"),
                ("c","collapse_all","Collapse All"),
                ("e","expand_all","Expand All"),
                ("s", "show_full_stats", "Full Stats"),
                ("j", "show_injuries", "Show Injuries"),
                ("l", "select_league", "Select League"),
                ("h", "toggle_help", "Show Help"),
                ]
    CSS_PATH = "appstyle.tcss"


    def __init__(self):
        super().__init__()
        self.YEAR_SELECT = af.YEAR
        self.league_selected = 0
        self.block_counter = 0
        #create a dict of all list of fixtures to reference them later
        self.blocklist = {}
        self.list_of_blocks = []
        self.selec_match = None
        self.last_focus_id = None
        self.memory_standings = None  # Memory of the standings in list of dict
        self.id_focused = "main_container" #Memory of the id of the focused widget
        self.injury_box_visible = False  # Flag per tracciare lo stato del box infortuni

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
        
        # Add championship selection dropdown
        league_options = []
        for key, value in af_map.items():
            league_options.append(f"{key}: {value['name']} ({value['country']})")
        # Create the OptionList with all options
        self.leaguebox = OptionList(*league_options, id="leaguebox")
        self.leaguebox.border_title = "Select Championship"
        yield self.leaguebox
        
        # Add league actions menu
        self.league_actions = OptionList(
            "Match of the day", 
            "Match Shift",
            "Standing",
            "Top Player score",
            "Top Player assist",
            "Exit",
            id="league_actions"
        )
        self.league_actions.border_title = "League Actions"
        yield self.league_actions
        
        # Add match shift input box
        self.shift_days_input = Input(id="shift_days_input", name="shift_days_input", placeholder="Days (+ or -)")
        yield self.shift_days_input
        
        #create an info box to show a varius texts
        # self.infobox = Static("info text to print",id="infobox")
        # yield Vertical(self.infobox,Button("ok",id="ok_info_button"),id="infolayout")
        self.select_todo_box = OptionList("EVENT TABLE","MATCH STATS","PREDICTION","FORM.LINEUPS","EXIT",id="select_todo_box")
        yield self.select_todo_box
        self.compare_text_box = Static("TEXt TEAM TO COMPARE",id="compare_text_box")
        self.compare_teams_box_hor = HorizontalScroll(self.compare_text_box)
        self.compare_teams_box = ScrollableContainer(self.compare_text_box,id="compare_teams_box")
        yield self.compare_teams_box
        self.injury_players_text = Static("INJURIES",id="injury_players_text")
        self.injury_players_box = ScrollableContainer(self.injury_players_text,id="injury_players_box")
        self.injury_players_box.styles.visibility = "hidden" # Imposta la visibilità iniziale a hidden
        yield self.injury_players_box
        
        # Add help window
        tabmap=table_af_map()
        formatted_tabmap = tabmap.split("\n")[0] + "\n" +"\n".join("            " + line for line in tabmap.split("\n")[1:])
        HELPTEXT=f"""
        
        GOAL MASTER {APPVERSION}
        
        KEYBOARD SHORTCUTS:
        
        q - Exit the application
        y - Change year of the selected football season
        i - Insert a manual command
        l - Open/close the league selection menu
        j - View player injuries for the selected match
        r - Remove the last displayed block
        c - Collapse all displayed sections
        e - Expand all displayed sections
        s - Show complete team statistics
        h - Toggle this help window

        INPUT BOX COMMANDS:
        -LIVE - show live matches define in ApiFootball and function get_fixture_live
        -HELP - show this help
        -STATUS - show status of api calls
        -EXIT - exit the app
        -LEAGUE -args:
            -S - standings
               - ALL - all groups standings if league has groups
               - #GROUPNUMBER - specific groups standings if league has groups
               - UPDATE - update standings and not call from existing standings on disk
            -T - timeshift days (example 1 is from today to today+1, or -1 is from today to today-1)
            -TOP 'S' - top scorers 'A' - top assists
        REPORT args:
            args - create a mergded report of all prediction of a league in pdf format
        
        AVAILABLE LEAGUES:
        
        {formatted_tabmap}
        """
        self.help_text = Static(HELPTEXT, id="help_text")
        self.help_box = ScrollableContainer(self.help_text, id="help_box")
        self.help_box.border_title = "COMMAND HELP"
        self.help_box.styles.width = "80%"
        self.help_box.styles.height = "80%"
        self.help_box.styles.dock = "top"
        self.help_box.styles.margin = (2, 2, 2, 2)
        self.help_box.styles.padding = (1, 1, 1, 1)
        self.help_box.styles.border = ("solid", "white")
        self.help_box.styles.background = "black"
        # content_align expects two values (horizontal, vertical)
        self.help_box.styles.align = ("center", "middle") 
        self.help_box.display = False  # Initially hidden
        yield self.help_box

    def find_league(self,league):
            #find name of league with de id of league
        for k,v in af_map.items():
            if v["id"] == self.league_selected:
                league_name = f"{af_map[k]["name"]} Country: {af_map[k]["country"]}"
                break
        return league_name

    #create block to show the current standings of the league
    def add_block_standings(self,league,text="text to print",group=0,update=False):
        s = af.get_list_standings(self.league_selected,update)
        if group =="all":
            standings = [af.get_table_standings(x) for x in s]
        else:
            standings = [af.get_table_standings(s[group])]
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
        #self.query_one(f"#{block_id}").focus()
        self.query_one("#main_container").scroll_end()
    def add_block_fixture(self,datefrom,dateto,live=False):
        #self.input_box.styles.visibility = "hidden" # Hide the input box
        fixtures=af.get_list_fixtures(self.league_selected,datefrom,dateto,live)
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
        #list_fixtures.focus()
        #scrool maioncontainer on botton of list view
        self.query_one("#main_container").scroll_end()
        self.set_timer(0.1, lambda: list_fixtures.focus())
        #list_fixtures.focus()
        #self.query_one(f"#{block_id}_fixtures").focus()
    def add_block_events_match(self,id_fixture,team1,team2):
        """
        Add a block with the events of the match.
        
        Args:
            id_fixture: ID of the fixture
            team1: Name of the first team
            team2: Name of the second team
        """
        
        af = api_football.ApiFootball()
        
        #self.input_box.styles.visibility = "hidden" # Hide the input box
        events_table = af.get_table_event_flow(id_fixture)
        
        # Check if there are any events to display - now properly checking Table object
        if not events_table or (isinstance(events_table, Table) and len(events_table.rows) == 0):
            self.notify("Non ci sono eventi da visualizzare", severity="warning", timeout=5, title="Nessun evento")
            return
        
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
        #check if match has started
        if self.selec_match.status in ["NS","RS"]: #not started or resulted
            self.notify("Match not started", severity="warning", timeout=5, title="Statistics not available")
            return
        
        af = api_football.ApiFootball()
        
        #self.input_box.styles.visibility = "hidden" # Hide the input box
        stats_table=af.print_table_standings(id_fixture)
        
        # Check if stats table exists and has content
        if not stats_table or (isinstance(stats_table, Table) and len(stats_table.rows) == 0):
            self.notify("Non ci sono statistiche da visualizzare", severity="warning", timeout=5, title="Nessuna statistica")
            return
            
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        self.query_one("#main_container").mount(Collapsible(Static(stats_table),
                                                             id=block_id,title="Statistic Match: "+team1+" vs "+team2,
                                                             collapsed=False)) #mount block and list_fixtures)
        self.query_one("#main_container").scroll_end()

    def add_block_prediction(self,league_id,id_fixture,team1,team2,prompt,team1_id,team2_id):
        #self.input_box.styles.visibility = "hidden" # Hide the input box
        json_file = "predictions.json"  # Usa il percorso diretto invece di gm.PREDICTION_FILE_DB
        id_fixture = str(id_fixture) #convert to string
        
        # Aggiunta log per debug
        self.notify(f"Cercando la previsione per id_fixture: {id_fixture}", severity="info", timeout=5)
        
        predictions = {}
        # Check if the file exists
        if not os.path.exists(json_file):
            self.notify(f"File {json_file} non trovato, creazione nuovo file", severity="info", timeout=5)
            predictions = {}  # Create an empty dictionary if the file doesn't exist
        else:
            try:
                # Load the existing predictions from the file
                with open(json_file, "r", encoding="utf-8") as f:
                    predictions = json.load(f)
                    # Aggiunta log per debug
                    self.notify(f"Caricato file con {len(predictions)} previsioni", severity="info", timeout=3)
            except json.JSONDecodeError:
                self.notify(f"Errore nel decodificare il file JSON, creazione nuovo file", severity="error", timeout=5)
                predictions = {}

        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        table_stats=af.get_standings(league_id)
        composed_prompt = f"The match is between {team1} vs {team2}, and view this standing: {table_stats}"
        
        # Aggiunta log per debug
        if id_fixture in predictions:
            self.notify(f"Trovata previsione esistente per {team1} vs {team2}", severity="info", timeout=3)
            prediction = predictions[id_fixture]
        else:
            self.notify(f"Generazione nuova previsione per {team1} vs {team2}", severity="info", timeout=3)
            # Il resto del codice rimane invariato
            rs1=(af.get_team_statistics(team1_id,league_id))
            rs2=(af.get_team_statistics(team2_id,league_id))
            ts1,ts2=gm.TeamStats(),gm.TeamStats()
            if (rs2 is not None) and (rs1 is not None):
                ts1.Charge_Data(rs1)
                ts2.Charge_Data(rs2)
            else:
                self.notify(f"Unable to get statistics for {team2} or {team1}", severity="error", timeout=5)
                return
            big_team_stats=af.print_table_compareteams(ts1,ts2)
            stats_prediction=f"This is data of prediction by agency between {team1} vs {team2}:{af.get_prediction(id_fixture)} and data of detailed statistics of both teams {big_team_stats}"
            preprompt="""
                Read data of prediction of this maatch, and analyze it. Stats of singol team, historical statistics of both teams.
                Match passed h2h of both teams. Show this data in table format.
                    """
            translate=f"Write this analysis in {languege}"
            prediction=gemini_ai.gemini_ai_call(translate+composed_prompt+stats_prediction+preprompt+prompt)
            #save in pdf this prediction
            save_prediction_pdf(id_fixture,prediction)
            # Save the updated predictions back to the JSON file with indentation for readability
            predictions[id_fixture] = prediction
            try:
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(predictions, f, indent=4, ensure_ascii=False)
                self.notify(f"Previsione salvata nel file {json_file}", severity="info", timeout=3)
            except Exception as e:
                self.notify(f"Errore nel salvare la previsione: {str(e)}", severity="error", timeout=5)
    
        self.query_one("#main_container").mount(Collapsible(Static(Markdown(prediction),classes="predictions"),
                                                            id=block_id,title="Prediction Match: "+team1+" vs "+team2,
                                                            collapsed=False)) #mount block and list_fixtures)
        self.query_one("#main_container").scroll_end()

    def add_block_formations(self,id_fixture,team1,team2):
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        #f1,f2=af.ApiFootball().get_formation_teams(id_fixture)
        formtext=af.print_table_formations(id_fixture)
        self.query_one("#main_container").mount(Collapsible(Static(formtext),id=block_id,title=f"Formations: {team1} vs {team2}",collapsed=False))
        self.query_one("#main_container").scroll_end()

    def add_block_help(self):
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        tabmap=table_af_map()
        formatted_tabmap = tabmap.split("\n")[0] + "\n" +"\n".join("            " + line for line in tabmap.split("\n")[1:])
        HELPTEXT=f"""

        GOAL MASTER {APPVERSION}

        KEYBOARD SHORTCUTS:

        TAB - Switch between input and select todo boxes
        ENTER - Add new todo
        Press r - Remove focused block

        INPUT BOX:
        command:
        -LIVE - show live matches define in ApiFootball and function get_fixture_live
        -HELP - show this help
        -STATUS - show status of api calls
        -EXIT - exit the app
        -LEAGUE -args:
            -S - standings
               - ALL - all groups standings if league has groups
               - #GROUPNUMBER - specific groups standings if league has groups
               - UPDATE - update standings and not call from existing standings on disk
            -T - timeshift days (example 1 is from today to today+1, or -1 is from today to today-1)
            -TOP 'S' - top scorers 'A' - top assists
        REPORT args:
            args - create a mergded report of all prediction of a league in pdf format
        
        AVAILABLE LEAGUES:
        
        {formatted_tabmap}

        Press q - Exit


        """
        self.query_one("#main_container").mount(Collapsible(Static(HELPTEXT),id=block_id,title="Help",collapsed=False))
        self.query_one("#main_container").scroll_end()

    def add_block_topscorers(self,idleague,assists=False):
        self.block_counter += 1 # Increment the block counter
        block_id = f"block_{self.block_counter}" # Create a unique block id
        tabmap=af.table_top_scores(idleague,assists)
        nameleague=self.find_league(idleague)
        mode="Assists" if assists else "Scorers"
        self.query_one("#main_container").mount(Collapsible(Static(tabmap),id=block_id,title=f"Top {mode} for {nameleague} for year {af.YEAR}",collapsed=False))
        self.query_one("#main_container").scroll_end()

    def on_mount(self):
        #self.query_one("#input").styles.visibility = "hidden" #
        self.input_box.display = False # Hide the input box
        #self.select_todo_box.styles.visibility = "hidden" # hide the select todo box
        self.select_todo_box.display = False
        self.leaguebox.display = False # Hide the league selection box initially
        self.league_actions.display = False # Hide the league actions menu initially
        self.shift_days_input.display = False # Hide the shift days input box initially
        self.update_title()
        # self.boxmessage = self.query_one("#infolayout")
        # self.boxmessage.styles.visibility = "hidden"
        self.query_one("#main_container").focus()

    def update_title(self):
        """Update the application title with current context including selected match if any."""
        if self.selec_match:
            match_info = f" - {self.selec_match.home_team} vs {self.selec_match.away_team}"
            if hasattr(self.selec_match, 'status') and self.selec_match.status:
                status_map = {
                    "NS": "Not Started",
                    "TBD": "To Be Decided",
                    "1H": "1st Half",
                    "HT": "Half Time", 
                    "2H": "2nd Half",
                    "ET": "Extra Time",
                    "P": "Penalty",
                    "FT": "Finished",
                    "AET": "After Extra Time",
                    "PEN": "Penalties",
                    "BT": "Break Time",
                    "SUSP": "Suspended",
                    "INT": "Interrupted",
                    "PST": "Postponed",
                    "CANC": "Cancelled",
                    "ABD": "Abandoned",
                    "AWD": "Technical Loss",
                    "WO": "WalkOver",
                }
                status = status_map.get(self.selec_match.status, self.selec_match.status)
                match_info += f" [{status}]"
        else:
            match_info = ""
        
        self.title = f"GOAL MASTER {APPVERSION} YEAR:{af.YEAR} CALLS:{af.remains_calls}{match_info}"

    # async def on_focus(self, event):
    #     self.last_focus_id = event.app.focused.id if event.app.focused else None
    #     #create a list of id of focus widgets
    #     #self.last_focus_id = event.id
    #     self.title = self.last_focus_id if self.last_focus_id else "GOAL MASTER"

    def on_key(self, event: Key):
        if event.key == "i":
            #self.input_box.styles.visibility = "visible"
            self.input_box.display = True
            self.input_box.focus()
            self.id_focused = self.focused.id
        elif event.key == "y":
            self.yearsbox.display = True
            self.yearsbox.focus()
            self.id_focused = self.focused.id
        elif event.key == "l":
            # Controlla se il menu è già visibile e in tal caso lo nasconde
            if self.leaguebox.display:
                self.leaguebox.display = False
            else:
                self.leaguebox.display = True
                self.leaguebox.focus()
                self.id_focused = self.focused.id
        elif event.key == "r" and self.block_counter > 0:
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
        elif event.key == "c":
            self.action_collapse_or_expand(True)
        elif event.key == "e":
            self.action_collapse_or_expand(False)
        elif event.key == "space":
            # If the focused widget is an OptionList and its id is in the list of blocks (match lists)
            if isinstance(self.focused, OptionList) and self.focused.id in self.list_of_blocks:
                # Get the currently highlighted option index
                highlighted_index = self.focused.highlighted
                
                if highlighted_index is not None:
                    # Get the match from the blocklist
                    self.selec_match = self.blocklist[self.focused.id][highlighted_index]
                    self.id_focused = self.focused.id
                    
                    # Show the action menu and focus on it
                    # self.select_todo_box.display = True
                    # self.select_todo_box.focus()
                    
                    # Notify and update title
                    self.notify(f"Selected match: {self.selec_match.home_team} vs {self.selec_match.away_team}", 
                               severity="info", timeout=3)
                    self.update_title()
        # elif event.key == "h":
        #     self.action_toggle_help()
    #button pressed

    def action_insert_command(self):
        #self.input_box.styles.visibility = "visible" if self.input_box.styles.visibility == "hidden" else "hidden"
        self.compare_teams_box.styles.visibility = "hidden"
        self.input_box.display = True
        self.input_box.focus()
    #action show injuries
    def action_show_injuries(self):
        if self.selec_match is None:
            self.notify("No match selected",severity="warning",timeout=5)
            return
            
        # Genero la tabella degli infortuni
        injury_table = af.generate_injury_table(self.selec_match.id_league,self.selec_match.date[:10],self.selec_match.id)
        
        # Incremento il contatore dei blocchi
        self.block_counter += 1
        
        # Creo un ID unico per questo box basato sul contatore
        block_id = f"block_{self.block_counter}"
        
        # Creo un Collapsible contenente la tabella degli infortuni e lo aggiungo al container principale
        self.query_one("#main_container").mount(
            Collapsible(
                Static(injury_table),
                id=block_id,
                title=f"Injuries Players: {self.selec_match.home_team} vs {self.selec_match.away_team}",
                collapsed=False
            )
        )
        
        # Notifica l'aggiunta del nuovo blocco
        self.notify("Injuries block added", severity="information", timeout=2)
        
        # Scorro alla fine del container per mostrare il nuovo box
        self.query_one("#main_container").scroll_end()

    def action_change_year(self):
        self.yearsbox.styles.visibility = "visible" if self.yearsbox.styles.visibility == "hidden" else "hidden"
        self.yearsbox.focus()
    def action_collapse_or_expand(self, collapse: bool) -> None:
        for child in self.walk_children(Collapsible):
            child.collapsed = collapse
    def action_show_full_stats(self):
        #validate if a match is selected
        if self.selec_match is None:
            self.notify("No match selected",severity="warning",timeout=5)
            return
        self.compare_teams_box.styles.visibility = "visible" if self.compare_teams_box.styles.visibility == "hidden" else "hidden"
        self.compare_teams_box.focus()
        r1=af.get_team_statistics(self.selec_match.id_home_team,self.selec_match.id_league)
        r2=af.get_team_statistics(self.selec_match.id_away_team,self.selec_match.id_league)
        t1,t2=gm.TeamStats(),gm.TeamStats()
        t1.Charge_Data(r1)
        t2.Charge_Data(r2)
        text_stat_to_show = af.print_table_compareteams(t1,t2)
        self.compare_text_box.update(text_stat_to_show)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "shift_days_input":
            try:
                days = int(event.value)
                if -150 <= days <= 150:
                    if days >= 0:
                        dfrom = datetime.now().date()
                        dto = datetime.now().date() + timedelta(days=days)
                    else:
                        dfrom = datetime.now().date() + timedelta(days=days)
                        dto = datetime.now().date()
                    
                    self.add_block_fixture(dfrom, dto)
                else:
                    self.notify("Days must be between -150 and 150", severity="error", timeout=5)
            except ValueError:
                self.notify("Invalid input. Please enter a number.", severity="error", timeout=5)
            
            # Hide the shift days input box and return focus to previous element
            self.shift_days_input.display = False
            self.shift_days_input.value = ""
            self.query_one(f"#{self.id_focused}").focus()
            return
            
        #validate di input is not void
        if event.value == "":
            return
        
        try:
            command = shlex.split(event.value.upper()) # Split the input string into a list of words
        except ValueError as e:
            # Handle the case where shlex.split fails due to unclosed quotes or escape characters
            self.notify(f"Invalid command syntax: {str(e)}", severity="error", timeout=5)
            self.input_box.display = False
            return
            
        #hide input box
        #self.input_box.styles.visibility = "hidden"
        #check if command is valid
        if command[0] == "REPORT":
            if len(command) < 1:
                self.notify("Invalid command",severity="warning",timeout=5)
                return
            elif command[1] not in af_map:
                self.notify("Invalid command",severity="warning",timeout=5)
                return
            lf=af.get_list_fixtures(af_map[command[1]]["id"],datetime.now().date(),datetime.now().date())
            lf_ids = [x.id for x in lf]
            if merge_pdfs(af_map[command[1]]["id"],lf_ids):
                self.notify("Report generated",severity="success",timeout=5)
            else:
                self.notify("Report not generated",severity="warning",timeout=5)
            self.input_box.display = False
            return
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
        if command[0] == "STATUS":
            #notify apicalls used
            self.input_box.display = False #hide input box
            self.notify(f"APICALLS USED: {100-af.remains_calls}",severity="warning",timeout=7,title="STATUS")
            #update title of app
            self.title = f"GOAL MASTER {APPVERSION} YEAR:{af.YEAR} CALLS:{af.remains_calls}"
            return
        if command[0] in af_map:
            self.league_selected = af_map[command[0]]["id"]
            #check if command is valid
            if len(command) == 1:
                self.notify(f"insert options command for {self.find_league(self.league_selected)}",severity="error",timeout=10,title="SYNTAX ERROR")
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
                    elif command[2] == "UPDATE": #call function to update standings without checking if exist
                        self.add_block_standings(self.league_selected,group="all",update=True)
                    #cheif if command[2] is a number between 0 and 9 but w/o convert it to int
                    elif command[2].isdigit():
                        self.add_block_standings(self.league_selected,group=int(command[2]))
                        #self.show_message("error command syntax",titlebox="SYNTAX ERROR")
                    else:
                        self.notify("error command syntax or command not found",severity="error",timeout=5,title="SYNTAX ERROR")
            elif command[1] == "-T":
                if len(command) < 3:
                    command.append("0")  #default value for days
                #check if we have 4 parameters and if it is a "REPORT"
                # if len(command) < 4 and ((command[2] == "REPORT") or (command[3] == "REPORT")):
                #     self.notify("selected command report for id_league {command[0]}",severity="info",timeout=10,title="selected report")
                #     return
                # else:
                #     self.notify("error command syntax or command not found",severity="error",timeout=5,title="SYNTAX ERROR")
                #     return
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
            elif command[1] == "-TOP":
                #print top scorers for league
                if len(command) < 3:
                    self.notify("insert options command for top scorers",severity="error",timeout=10,title="SYNTAX ERROR")
                    return
                else:
                    if command[2] == "S": #selected top scorers
                        self.add_block_topscorers(self.league_selected)
                    elif command[2] == "A": #selected top assists
                        self.add_block_topscorers(self.league_selected,assists=True)
                    else:
                        self.notify("must specify 'A' for top assists or 'S' for top scorers",severity="error",timeout=10,title="SYNTAX ERROR")
                        return
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
            self.yearsbox.display = False
            af.YEAR = selected_option
            self.update_title()
            self.query_one(f"#{self.id_focused}").focus()
        
        elif event.option_list.id == "leaguebox":
            # Get the selected league key from the option text
            option_text = event.option_list.get_option_at_index(event.option_index).prompt
            league_key = option_text.split(":")[0].strip()
            
            if league_key in af_map:
                self.league_selected = af_map[league_key]["id"]
                self.league_name = af_map[league_key]["name"]
                self.notify(f"Selected: {af_map[league_key]['name']}", severity="info", timeout=3)
                
                # Hide the league selection box
                self.leaguebox.display = False
                
                # Show the league actions menu
                self.league_actions.border_title = f"Actions for {self.league_name}"
                self.league_actions.display = True
                self.league_actions.focus()
            else:
                # Hide the league selection box and return focus to previous element
                self.leaguebox.display = False
                self.query_one(f"#{self.id_focused}").focus()
        
        elif event.option_list.id in self.list_of_blocks:
            self.selec_match = self.blocklist[event.option_list.id][event.option_index]
            self.id_focused = event.option_list.id
            self.select_todo_box.display = True
            #focus on select todo box
            self.select_todo_box.focus()

            self.notify(self.selec_match.home_team+" vs "+self.selec_match.away_team, severity="info", timeout=5)
            # Update the title with selected match info
            self.update_title()
        
        elif event.option_list.id == "league_actions":
            option_index = event.option_index
            
            # Hide the league actions menu
            self.league_actions.display = False
            
            if option_index == 0:  # Match of the day
                # Show matches for today
                dfrom = datetime.now().date()
                dto = datetime.now().date()
                self.add_block_fixture(dfrom, dto)
                self.query_one(f"#{self.id_focused}").focus()
            
            elif option_index == 1:  # Match Shift
                # Show the shift days input box
                self.shift_days_input.display = True
                self.shift_days_input.focus()
            
            elif option_index == 2:  # Standing
                # Show standings
                self.add_block_standings(self.league_selected)
                self.query_one(f"#{self.id_focused}").focus()
            
            elif option_index == 3:  # Top Player score
                # Show top scorers
                self.add_block_topscorers(self.league_selected, assists=False)
                self.query_one(f"#{self.id_focused}").focus()
            
            elif option_index == 4:  # Top Player assist
                # Show top assists
                self.add_block_topscorers(self.league_selected, assists=True)
                self.query_one(f"#{self.id_focused}").focus()
            
            elif option_index == 5:  # Exit
                # Return focus to previous element
                self.query_one(f"#{self.id_focused}").focus()
        
        elif event.option_list.id == "select_todo_box":
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
                injuried_players = af.get_list_injuries_by_date(self.selec_match.id_league,self.selec_match.date[:10])
                top_score_players = af.get_top_scores(self.selec_match.id_league)
                top_assists_players = af.get_top_assists(self.selec_match.id_league)
                
                # Check if there are injuries for this specific match
                fixture_id = str(self.selec_match.id)
                if fixture_id in injuried_players:
                    p_inj_fixture = json.dumps(injuried_players[fixture_id], indent=4)
                else:
                    # No injuries for this match
                    p_inj_fixture = json.dumps({}, indent=4)
                
                prompt_request = f"""
                Analyze the match between {self.selec_match.home_team} and {self.selec_match.away_team}.
                Try to analyze the match between the two teams, providing a precise context in which they
                will face each other, comparing their statistical performance in the league.
                Present this data using comparative tables where possible.
                Analyze well the behavior and performance of the teams at home and away, and base your judgment on this,
                which should be a calculated prediction 1 X 2, and where you are unsure, also provide a double chance
                (for example, 1X, X2, 12). When you are in doubt, you can also provide a double chance (for example, 12 and not 1X or X2 if you
                think that the match will end in a draw necessarily). Additionally, separate with a line the next judgment on how many
                goals the teams might score and whether it's likely to be GG (both teams to score) or NG
                (no goals from one or both teams).
                Keep in mind this list of unavailable players as well {p_inj_fixture}, and try to determine if they are
                important players for either team by considering if they have contributed with assists
                or goals in the current season by checking the top players by assists and goals {top_assists_players} and {top_score_players} update. 
                If the player is not in the list, not invent or search for the player on internet if you not find it, because you wrong evertimes the
                judgment of the player in the match. At the begin  of report not speak abaout the your prediciotn example with say "sure" or "certanly" etc etc,
                but only the prediction and the reason of it and the Title of toy report in H1.
                """
                # if not (self.selec_match.status in ["NS","RS"]): #not started or resulted
                #     self.notify("Match not started",severity="warning",timeout=5)
                if self.selec_match.status == "FT" and self.selec_match.prediction == False:
                    self.notify("Match finished",severity="warning",timeout=5,title="Prediction not available")
                elif self.selec_match.status in ["1H","2H","HT","P"]: #live prediction
                    self.notify("Match live",severity="warning",timeout=5,title="Prediction not available")
                    pass
                else:  #not live prediction
                    self.notify(f"Analyze prediction... {self.selec_match.home_team} vs {self.selec_match.away_team}",severity="info",timeout=8,title="PREDICT IN PROGRESS")
                    self.add_block_prediction(self.league_selected,self.selec_match.id,self.selec_match.home_team,self.selec_match.away_team,prompt_request,self.selec_match.id_home_team,self.selec_match.id_away_team)
                    #update flag prediction match to true
                    self.selec_match.prediction = True
            if event.option_index == 3:  #selected add block formations of selected match
                if not (self.selec_match.status in ["NS","RS"]): #not started or resulted
                    self.add_block_formations(self.selec_match.id,self.selec_match.home_team,self.selec_match.away_team)
                else:
                    self.notify("Match not started",severity="warning",timeout=5)
                    self.focused.focus()

                    return
            if event.option_index == 4:  #exit
                self.query_one(f"#{self.id_focused}").focus()
                return

    def action_toggle_help(self):
        """Toggle the visibility of the help box."""
        if self.help_box.display:
            self.help_box.display = False
            # Restore focus to previously focused element if possible
            if hasattr(self, 'id_focused') and self.id_focused:
                try:
                    self.query_one(f"#{self.id_focused}").focus()
                except:
                    pass
        else:
            # Store current focus before showing help
            if self.focused:
                self.id_focused = self.focused.id
            self.help_box.display = True
            self.help_box.focus()

if __name__ == "__main__":
    app = goalmasterapp().run()
