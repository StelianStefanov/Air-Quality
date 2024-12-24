from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Label
from textual.widgets import Static
from textual.reactive import reactive

from src.utilities import Utilities


class FooterLayout(Footer):

    def compose(self) -> ComposeResult:

        for widget in super().compose():
            yield widget
        yield Static("", id="footer_right_static")
