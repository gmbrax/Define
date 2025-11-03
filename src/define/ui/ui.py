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
        self.console.print("This Application requires Merriam-Webster Key for both Dictionary and Thesaurus")
        print("Please enter your Merriam-Webster Dictionary API:", end='')
        dictionary_api_key = input()
        print(f"\033[A\rPlease enter your Merriam-Webster Dictionary API:{' ' * len(dictionary_api_key)}\rPlease enter your Merriam-Webster Dictionary API:", end='')
        while dictionary_api_key == '':
            self.console.print("[bold red]Invalid API Key: Can't be empty [/bold red]")
            print("Please enter your Merriam-Webster Dictionary API:", end='')
            dictionary_api_key = input()
            print(f"\033[A\rPlease enter your Merriam-Webster Dictionary API:{' ' * len(dictionary_api_key)}\rMerriam-Webster Dictionary API", end='')
        print("\n")
        self.__parent.config.set_data_dict({"DICTIONARY KEY":dictionary_api_key})

        print("Please enter your Merriam-Webster Thesaurus API:", end='')
        thesaurus_api_key = input()
        print(
            f"\033[A\rPlease enter your Merriam-Webster Thesaurus API:{' ' * len(thesaurus_api_key)}\rPlease enter your Merriam-Webster Thesaurus API:",
            end='')
        while thesaurus_api_key == '':
            self.console.print("[bold red]Invalid API Key: Can't be empty [/bold red]")
            print("Please enter your Merriam-Webster Thesaurus API:", end='')
            thesaurus_api_key = input()
            print(
                f"\033[A\rPlease enter your Merriam-Webster Thesaurus API:{' ' * len(thesaurus_api_key)}\rPlease enter your Merriam-Webster Thesaurus API:",
                end='')
        print("\n")
        self.__parent.config.set_data_dict({"THESAURUS KEY": thesaurus_api_key})
        self.__parent.config.write_config()
        exit(0)

    def check_configuration(self):
        if not self.__parent.is_configured:
            self.console.print("[bold red]Please configure before running this program.[/bold red]")
            exit(1)

    def run(self):


        self.console.print("[bold]Define[/bold] [italic white]V.0.0.1[/italic white ] by Gustavo Henrique S. S. de Miranda\n")
        self.console.print("Definitions and thesaurus data provided by Merriam-Webster, Inc. © Merriam-Webster, Inc. All rights reserved.")
        self.console.print("This application uses data from Merriam-Webster's Dictionary and Thesaurus APIs, referenced with permission.")
        self.console.print("\n")

        if self.check_configure_mode():
            self.configure()

        if self.__parent.run_mode:
            self.check_configuration()
