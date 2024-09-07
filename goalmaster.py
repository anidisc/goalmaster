import gemini_ai
import api_football as af
from textual.app import App
from textual.widgets import Header, Footer, Button, Static, Tree, ListView,ListItem
from textual.containers import ScrollableContainer,Vertical
from rich import print as rich_print


APPVERSION = "0.0.1"

#class for structure data of a soccer team
class goalmasterapp(App):
    BINDINGS = [("q", "quit", "Quit"),
                ("y", "change_year", "Change Year")]
    CSS = """
        #Screen {
            align: center middle;
            layers: below above above2;
        }

        #siderbar{
            dock: left;
            background: blue;
            color: white;
            width: 35%;
            height: 100%;
            layer: above;
            margin:1;
    }
        #static_standings{
            width: 100%;
            height: 100%;
            layer: below;
        }

        """
    def __init__(self):
        super().__init__()
        self.YEAR_SELECT = af.ApiFootball().YEAR

    def compose(self):
        #list of years to 2015 to 2024
        list_years=ListView(id="list_years",
                            *[ListItem(Static(str(y),id=f"list_year_{y}")) for y in range(2015,2025)])
        #title of the sidebar
        title_list=Static("Select the year",id="title_list")
        yield Header()
        self.sidebar=ScrollableContainer(
            Vertical(title_list,list_years),name="sidebar",id="sidebar")
        yield self.sidebar
        yield Footer()
        yield Static("Table",id="static_standings")
        yield Button("Get Table standings",id="get_table_standings")
    
    def on_action_change_year(self):
        self.sidebar.styles.visibility = "visible"
        self.query_one("#title_list", Static).update("Select the year")
        self.query_one("#sidebar", Static).update(self.sidebar)

    def on_button_pressed(self, event):
        if event.button.id == "get_table_standings":
            table = af.ApiFootball().get_table_standings(135)
            self.query_one("#static_standings", Static).update(table)
            self.sidebar.styles.visibility = "hidden"

        

if __name__ == "__main__":
    app = goalmasterapp().run()

