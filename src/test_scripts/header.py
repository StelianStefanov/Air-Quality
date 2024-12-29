from textual.app import App, ComposeResult
from textual.widgets import Header


class Header(App):

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

    def on_mount(self) -> None:
        self.title = "Hello"
