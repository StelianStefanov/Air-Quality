"""Startup module"""

from src.display import Display


def main():
    app = Display()
    app.run()


if __name__ == "__main__":
    main()
