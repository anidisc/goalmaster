from textual.app import App, ComposeResult
from textual.widgets import OptionList,Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield OptionList("opzione1", "opzione2", "opzione3")
        yield Static("Seleziona una voce",id="output")

    def on_mount(self):
        self.option_list = self.query_one(OptionList)
        self.option_list.BINDINGS.append

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        selected_option = event.option.prompt
        self.query_one("#output", Static).update(f"Selezionata: {selected_option}")


  
if __name__ == "__main__":
    app = MyApp()
    app.run()