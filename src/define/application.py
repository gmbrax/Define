from define.ui import UI


class Application:

    def __init__(self):
        self.ui = UI(self)

    def run(self):
        print("hellord")