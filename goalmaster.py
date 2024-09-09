import gemini_ai
import api_football as af
from textual.app import App
from textual.widgets import Header, Footer, Button, Static, ListView, ListItem
from textual.containers import ScrollableContainer,Vertical
from rich import print as rich_print
from _datetime import datetime,timedelta


APPVERSION = "0.0.1"

#class for structure data of a soccer team
class goalmasterapp(App):
    BINDINGS = [("q", "quit", "Quit"),
                ("y", "change_year", "Change Year")]
    CSS_PATH = "appstyle.css"

    
    def __init__(self):
        super().__init__()
        self.YEAR_SELECT = af.ApiFootball().YEAR

    def compose(self):
        #list of years to 2015 to 2024
        self.list_years=ListView(
                            *[ListItem(Static(str(y),id="_"+str(y))) for y in range(2015,2024)],
                            id="list_y"
        )
        #list of match to select
        self.list_match=ListView(id="list_match",name="list_match")
        #title of the sidebar
        self.title_list=Static("Select the year",id="title_list",name="title_list")
        yield Header()
        self.sidebar=ScrollableContainer(self.title_list,self.list_years,name="sidebar_years",id="sidebar_years")
        self.box_of_matches=ScrollableContainer(Vertical(
                                                self.list_match,
                                                Static("match selezionato",id="ms"),
                                                name="box_of_matches",id="box_of_matches"))
        yield self.box_of_matches
        yield self.sidebar
        yield Footer()

    def action_change_year (self):
        self.sidebar.styles.visibility = "visible" if self.sidebar.styles.visibility == "hidden" else "hidden"
        if self.sidebar.styles.visibility == "visible":
            self.list_years.focus()
    def on_mount(self):
        self.sidebar.styles.visibility = "hidden"

    async def on_list_view_selected(self, event: ListView.Selected):
        #self.sidebar.styles.visibility = "hidden"
        #self.list_years.focus()
        selected_item = event.item.query_one(Static).renderable
        if event.list_view.id=="list_match":
            self.query_one("#ms",Static).update(f"selezionato {event.list_view.index}")
        elif event.list_view.id=="list_y":
            self.query_one("#title_list", Static).update(f"Select {selected_item}")
            matches=af.ApiFootball(2024).get_list_fixtures(135,datefrom=datetime.now().date()-timedelta(days=10),dateto=datetime.now().date())
            for m in matches:
                item=str(m)
                self.list_match.append(ListItem(Static(item)))
        #self.query_one("#sidebar", Static).update(self.sidebar)
  
         
    # def on_action_change_year(self):
    #     self.sidebar.styles.visibility = "visible"
    #     self.query_one("#title_list", Static).update("Select the year")
    #     self.query_one("#sidebar", Static).update(self.sidebar)

    # def on_button_pressed(self, event):
    #     if event.button.id == "get_table_standings":
    #         table = af.ApiFootball().get_table_standings(135)
    #         self.query_one("#static_standings", Static).update(table)
    #         self.sidebar.styles.visibility = "hidden"

        

if __name__ == "__main__":
    app = goalmasterapp().run()

