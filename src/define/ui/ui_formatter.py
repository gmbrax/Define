import textwrap
from rich.text import Text


from define.models import Entry, Definition


class Formatter:
    """Formata entradas para exibição"""

    def __init__(self, console_width: int):
        self.width = console_width

    def format_main_entry(self, entry: Entry) -> Text:
        """Formata entrada principal"""
        text = Text()

        # Header
        text.append(self._format_header(entry), style='bold green')

        # Etymology
        if entry.etymology:
            text.append('\n')
            text.append('Etymology: ', style='italic')
            text.append(entry.etymology)
            text.append('\n')

        # Definitions
        text.append('\nDefinitions:\n', style='bold')
        for definition in entry.definitions:
            text.append(self._format_definition(definition))

        # Quick summary
        if entry.short_summary:
            text.append('\nQuick summary:\n', style='bold')
            for summary in entry.short_summary:
                wrapped = textwrap.fill(f" - {summary}", self.width)
                text.append(wrapped + '\n')

        text.append('\n')
        return text

    def format_sub_entry(self, entry: Entry) -> Text:
        """Formata sub-entrada (compostos)"""
        text = Text()

        # Header simplificado
        parts = [entry.headword]
        if entry.homonym_num:
            parts.append(f"(homonym {entry.homonym_num})")
        if entry.part_of_speech:
            parts.append(f"[{entry.part_of_speech}]")

        title = ' '.join(parts)
        text.append(f"  └─ {title}\n", style='bold yellow')

        # Primeiro summary ou definição
        summary = ''
        if entry.short_summary:
            summary = entry.short_summary[0]
        elif entry.definitions:
            summary = entry.definitions[0].text

        if summary:
            wrapped = textwrap.fill(
                summary,
                width=self.width,
                initial_indent='      ',
                subsequent_indent='      '
            )
            text.append(wrapped + '\n')

        return text

    def _format_header(self, entry: Entry) -> str:
        """Formata header"""
        parts = [entry.headword]

        if entry.homonym_num:
            parts.append(f"(homonym {entry.homonym_num})")

        if entry.part_of_speech:
            parts.append(f"[{entry.part_of_speech}]")

        if entry.pronunciations:
            pron_texts = [p.text for p in entry.pronunciations if p.text]
            if pron_texts:
                parts.append(f"/{', '.join(pron_texts)}/")

        return ' '.join(parts) + '\n'

    def _format_definition(self, definition: Definition) -> Text:
        """Formata uma definição"""
        text = Text()

        # Texto principal
        wrapped_def = textwrap.fill(
            f" {definition.index}. {definition.text}",
            self.width
        )
        text.append(wrapped_def + '\n')

        # Exemplos
        if definition.examples:
            for example in definition.examples:
                text.append('    ', style='dim')
                text.append('Example: ', style='italic')
                wrapped_ex = textwrap.fill(
                    example,
                    width=self.width - 14,
                    initial_indent='',
                    subsequent_indent=''
                )
                text.append(wrapped_ex + '\n')

        # Synonyms
        if definition.synonyms:
            text.append('    ', style='dim')
            text.append('Synonyms: ', style='bold cyan')
            syns = ', '.join(sorted(set(definition.synonyms)))
            wrapped_syns = textwrap.fill(
                syns,
                width=self.width - 14,
                initial_indent='',
                subsequent_indent=''
            )
            text.append(wrapped_syns + '\n')

        # Related
        if definition.related:
            text.append('    ', style='dim')
            text.append('Related: ', style='bold blue')
            rels = ', '.join(sorted(set(definition.related)))
            wrapped_rels = textwrap.fill(
                rels,
                width=self.width - 14,
                initial_indent='',
                subsequent_indent=''
            )
            text.append(wrapped_rels + '\n')

        # Antonyms
        if definition.antonyms:
            text.append('    ', style='dim')
            text.append('Antonyms: ', style='bold red')
            ants = ', '.join(sorted(set(definition.antonyms)))
            wrapped_ants = textwrap.fill(
                ants,
                width=self.width - 14,
                initial_indent='',
                subsequent_indent=''
            )
            text.append(wrapped_ants + '\n')

        return text