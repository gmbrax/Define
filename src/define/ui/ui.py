from rich.console import Console
from define.ui import Formatter


class UI:
    def __init__(self, parent):
        self.__parent = parent
        self.console = Console()
        self.formatter = Formatter(self.console.size.width - 4)

    def check_configure_mode(self):
        if self.__parent.run_mode is False:
            self.console.print("[bold red]Running on Configuration Mode:[/bold red]")
            return True
        return False

    def configure(self):
        self.console.print("This Application requires Merriam-Webster Key for both Dictionary and Thesaurus\n")
        print("Please enter your Merriam-Webster Dictionary API:", end='')
        dictionary_api_key = input()
        print(
            f"\033[A\rPlease enter your Merriam-Webster Dictionary API:{' ' * len(dictionary_api_key)}\rPlease enter your Merriam-Webster Dictionary API:",
            end='')
        while dictionary_api_key == '':
            self.console.print("[bold red]Invalid API Key: Can't be empty [/bold red]")
            print("Please enter your Merriam-Webster Dictionary API:", end='')
            dictionary_api_key = input()
            print(
                f"\033[A\rPlease enter your Merriam-Webster Dictionary API:{' ' * len(dictionary_api_key)}\rMerriam-Webster Dictionary API",
                end='')
        print("\n")
        self.__parent.config.set_data_dict({"DICTIONARY KEY": dictionary_api_key})

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

    def check_if_word_argument_exists(self):
        if self.__parent.args.Word is None:
            return False
        return True

    def display_results(self, main_entries, sub_entries):
        """Exibe resultados formatados"""
        try:
            with self.console.pager(styles=True):
                # Entradas principais
                for entry in main_entries:
                    self.console.print(self.formatter.format_main_entry(entry))

                # Sub-entradas
                if sub_entries:
                    for entry in sub_entries:
                        self.console.print(self.formatter.format_sub_entry(entry))

                self.console.print('-' * self.formatter.width)

        except Exception as e:
            self.console.print(f"[bold red]Error displaying results: {e}[/bold red]")

    def run(self):
        self.console.print(
            "[bold]Define[/bold] [italic white]V.0.0.1[/italic white] by Gustavo Henrique S. S. de Miranda\n")
        self.console.print(
            "Definitions and thesaurus data provided by Merriam-Webster, Inc. © Merriam-Webster, Inc. All rights reserved.")
        self.console.print(
            "This application uses data from Merriam-Webster's Dictionary and Thesaurus APIs, referenced with permission.")
        self.console.print("\n")

        if self.check_configure_mode():
            self.configure()

        if self.__parent.run_mode:
            self.check_configuration()

        # Pega palavra
        if not self.check_if_word_argument_exists():
            word = self.console.input("Please type the word to Define: ")
        else:
            word = self.__parent.args.Word

        with self.console.status("[bold green]Fetching definitions...[/bold green]"):
            main_entries = []
            sub_entries = []

            # 🎯 FLUXO 1: Apenas Dicionário (-d)
            if self.__parent.args.dictionary and not self.__parent.args.thesaurus:
                dict_result = self.__parent.dictionary.fetch_and_process(word)

                if not dict_result:
                    self.console.print(f"[bold red]No dictionary results found for '{word}'[/bold red]")
                    return

                main_entries, sub_entries = dict_result
                # NÃO enriquece com thesaurus

            # 🎯 FLUXO 2: Apenas Thesaurus (-t)
            elif self.__parent.args.thesaurus and not self.__parent.args.dictionary:
                thes_result = self.__parent.thesaurus.fetch_and_process(word)

                if not thes_result:
                    self.console.print(f"[bold red]No thesaurus results found for '{word}'[/bold red]")
                    return

                main_entries, sub_entries = thes_result
                # Já vem processado do thesaurus

            # 🎯 FLUXO 3: Ambos (default, sem flags)
            else:
                dict_result = self.__parent.dictionary.fetch_and_process(word)

                if not dict_result:
                    self.console.print(f"[bold red]No results found for '{word}'[/bold red]")
                    return

                main_entries, sub_entries = dict_result
            if not (self.__parent.args.dictionary and not self.__parent.args.thesaurus):
                self.__parent.thesaurus.enrich_entries(word, main_entries)

        # Exibe resultados
        self.display_results(main_entries, sub_entries)