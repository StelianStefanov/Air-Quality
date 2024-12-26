from test_scripts.script import display_data
from test_scripts.script import display


def main():
    try:
        display_data()
    except KeyboardInterrupt:
        display.set_backlight(0)


if __name__ == "__main__":
    main()
