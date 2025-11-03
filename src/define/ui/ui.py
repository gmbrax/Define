from rich.console import Console


class UI:
    def __init__(self,parent):
        self.__parent = parent
        self.console = Console()

    def check_configure_mode(self):
        if self.__parent.run_mode is False:
            self.console.print("[bold red]Running on Configuration Mode:[/bold red]")
            return True
        return False

    def configure(self):
        exit(0)

    def check_configuration(self):
        if not self.__parent.is_configured:
            self.console.print("[bold red]Please configure before running this program.[/bold red]")
            exit(1)

    def run(self):
        if self.check_configure_mode():
            self.configure()

        self.console.print("[bold]Define[/bold] [italic white]V.0.0.1[/italic white ] by Gustavo Henrique S. S. de Miranda\n")
        self.console.print("Definitions and thesaurus data provided by Merriam-Webster, Inc. © Merriam-Webster, Inc. All rights reserved.")
        self.console.print("This application uses data from Merriam-Webster's Dictionary and Thesaurus APIs, referenced with permission.")
        self.console.print("\n")
        if self.__parent.run_mode:
            self.check_configuration()
