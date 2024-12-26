from dotenv import load_dotenv
import os


class MainConfig:
    def __init__(self):
        load_dotenv()

    @property
    def get_net_interfaces(self) -> list[str]:

        return os.getenv("NET_INTERFACES").split(",")

    @property
    def get_screen_title(self) -> str:
        return os.getenv("TITLE_SCREEN")


main_cnf = MainConfig()
