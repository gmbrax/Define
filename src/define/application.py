import argparse

from define.ui import UI
from define.utils import ConfigManager


class Application:

    def __init__(self):
        self.ui = UI(self)
        self.parser = None
        self.args = None
        self.is_configured = False
        self.config = ConfigManager()

    def setup(self)->None:
        if self.config.read_config() is not None:
            self.is_configured = True

        self.__validate_args()

    def __validate_args(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--configure","-c",action="store_true", help="Runs the configuration "
                                                                              "wizard")

        self.parser.add_argument("-d","--dictionary",action="store_true", help="Shows the dictionary "
                                                                               "definition")

        self.parser.add_argument("-t","--thesaurus",action="store_true", help="Shows the thesaurus"
                                                                              " definition")

        self.parser.add_argument("Word", nargs='?', type=str, help="Word to be defined")

        self.args = self.parser.parse_args()

        if self.args.configure and self.args.Word:
            self.parser.error("Cannot use --configure with a word")





    def run(self):
        print("hellord")