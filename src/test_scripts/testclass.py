import time


class Test:

    def __init__(self):
        self._is_setup = False
        self.counter = 0

    def setup(self):
        if not self._is_setup:
            self._is_setup = True
            print("Setup!")

    def run(self):
        self.setup()
        if self.counter < 3:
            print("Running!")
        self.counter += 1
        print(self.counter)


if __name__ == "__main__":
    test = Test()
    while True:
        test.run()
        time.sleep(1)
