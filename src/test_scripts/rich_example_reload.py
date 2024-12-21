# https://rich.readthedocs.io/en/stable/index.html
# python -m rich.emoji

import random
import time

from rich.live import Live
from rich.table import Table
from rich import box

emojies = ["high_brightness", "high_voltage", "thermometer", "fog", "skull", "rainbow", "umbrella_with_rain_drops"]


def generate_table() -> Table:
    """Make a new table."""

    table = Table(box=None, show_edge=False)
    table.add_column(width=30)
    table.add_column(width=30)
    table.add_column(width=30)

    for row in range(3):
        value = random.random() * 100
        table.add_row(
            f"{row} => :{random.choice(emojies)}:", f"{value:3.2f}", "[red]ERROR" if value < 50 else "[green]SUCCESS"
        )
    return table


# Do start program and load table
with Live(generate_table(), refresh_per_second=1) as live:

    while True:
        time.sleep(1)
        live.update(generate_table())
