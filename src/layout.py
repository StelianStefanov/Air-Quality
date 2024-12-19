from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.widgets import Label
from textual.widgets import Digits
import random


class GridLayoutExample(App):
    CSS_PATH = "grid_layout2.tcss"

    def compose(self) -> ComposeResult:

        yield Static(f"", classes="box some", id="f")
        # yield Label("Hello, world!", classes="box")
        yield Static("Two", classes="box", id="s")
        # yield Static("Three", classes="box")
        yield Digits("454545", classes="box", id="st")
        yield Static("Temp: 16C", classes="box", id="temp")
        yield Static("Five", classes="box")
        yield Static("Six", classes="box")
        yield Static("Seven", classes="box")
        yield Static("8888", classes="box")
        yield Static("9999", classes="box")

    def on_ready(self) -> None:
        self.update()
        self.set_interval(1, self.update)

    def update(self):
        self.query_one("#f").update(f"{random.randint(1, 432352563636346)}")
        self.query_one("#st").update(f"{random.randint(1, 1067)}")
        # self.query_one("#temp").update(f"Temp: {random.randint(1, 30)}C")


if __name__ == "__main__":
    app = GridLayoutExample()
    app.run()
