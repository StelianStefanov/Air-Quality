from dotenv import load_dotenv
import os


class MainConfig:
    def __init__(self):
        load_dotenv()

    @property
    def get_net_interfaces(self) -> list[str]:
        try:
            if os.getenv("NET_INTERFACES"):
                return os.getenv("NET_INTERFACES").split(",")
            else:
                raise ValueError("NET_INTERFACES is not defined in .env")
        except ValueError as e:
            print(e)

    @property
    def get_screen_title(self) -> str:
        try:
            return os.getenv("TITLE_SCREEN")
        except Exception as e:
            print(e)


main_cnf = MainConfig()
