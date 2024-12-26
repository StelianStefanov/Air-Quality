from textual.app import ComposeResult
from textual.widgets import Footer
from textual.widgets import Static


from src.utilities import Utilities


class FooterLayout(Footer):

    def compose(self) -> ComposeResult:

        for widget in super().compose():
            yield widget
        yield Static("", id="footer_right_static")
