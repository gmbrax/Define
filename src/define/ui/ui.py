from rich.console import Console


class UI:
    def __init__(self,parent):
        self.__parent = parent
        self.console = Console()

    def run(self):
        self.console.print("[bold]Define[/bold] [italic white]V.0.0.1[/italic white ] by Gustavo Henrique S. S. de Miranda\n")
        self.console.print("Definitions and thesaurus data provided by Merriam-Webster, Inc. © Merriam-Webster, Inc. All rights reserved.")
        self.console.print("This application uses data from Merriam-Webster's Dictionary and Thesaurus APIs, referenced with permission.")

