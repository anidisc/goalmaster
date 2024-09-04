import gemini_ai
import api_football as af
from textual.app import App
from textual.widgets import Header, Footer, Button, Static, Tree
from textual.containers import ScrollableContainer
from rich import print as rich_print


APPVERSION = "0.0.1"

#class for structure data of a soccer team
class goalmasterapp(App):
    def on_mount(self):
        self.title = f"GoalMaster {APPVERSION}"
    def compose(self):
        yield Header()
        yield ScrollableContainer(
            Button("get table standings", id="get_table_standings"),
            Button("get list standings", id="get_list_standings"),
        
            Static("testo",id="testo"),
            id="container",name="sidebar_years",id="sidebar_years")
        yield Footer()
        ye

    BINDINGS = [("q", "quit", "Quit")]

    def on_button_pressed(self, event):
        if event.button.id == "get_table_standings":
            table = af.ApiFootball().get_table_standings(135)
            #print in the Static widget
            self.query_one("#testo").update(table)
        if event.button.id == "get_list_standings":
            table = af.ApiFootball().get_list_standings(135)
            rich_print(table)
        

if __name__ == "__main__":
    app = goalmasterapp().run()