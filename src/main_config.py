class MainConfig:
    def __init__(self):
        pass

    @property
    def get_net_interfaces(self) -> list[str]:
        return ["eth0", "wlan0", "enp60s0"]

    @property
    def get_screen_title(self) -> str:
        return "Air Quality"


main_cnf = MainConfig()
